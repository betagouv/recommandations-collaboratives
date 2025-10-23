import django.dispatch
from actstream import action
from actstream.models import action_object_stream
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, pre_delete, pre_save
from django.dispatch import receiver
from notifications import models as notifications_models

from recoco import verbs
from recoco.apps.projects.utils import (
    notify_advisors_of_project,
    notify_members_of_project,
)
from recoco.apps.tasks import models as tasks_models
from recoco.apps.tasks.signals import action_created

from ..projects.utils import reactivate_if_necessary
from . import models
from .models import RecommendationNode
from .utils import (
    gather_annotations_for_message_notification,
    post_public_message_with_recommendation,
)

message_posted = django.dispatch.Signal()


@receiver(action_created)
def make_message_on_action_creation(sender, task, project, user, **kwargs):
    """Post a public message with the recommendation attached. This workaround is needed
    as long as we don't natively support recommendation handling from the chat interface.
    """
    if task.public is False:
        return

    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    post_public_message_with_recommendation(recommendation=task)


# In case of deletion
@receiver(pre_delete, sender=models.Message, dispatch_uid="message_hard_delete_logs")
@receiver(pre_save, sender=models.Message, dispatch_uid="message_soft_delete_logs")
def delete_activity_on_message_delete(sender, instance, **kwargs):
    if instance.deleted is None:
        return

    project_ct = ContentType.objects.get_for_model(instance)
    notifications_models.Notification.objects.filter(
        target_content_type=project_ct.pk, target_object_id=instance.pk
    ).delete()

    action_object_stream(instance).delete()


# Synchronize message/reco deletion
@receiver(
    post_delete,
    sender=models.RecommendationNode,
    dispatch_uid="reco_node_hard_delete_sync",
)
def delete_reco_on_node_delete(sender, instance, **kwargs):
    if instance.recommendation:
        instance.recommendation.delete()


@receiver(
    pre_save,
    sender=tasks_models.Task,
    dispatch_uid="reco_delete_message_sync",
)
def delete_message_on_reco_delete(sender, instance, **kwargs):
    if instance.deleted is None:
        return

    for node in RecommendationNode.objects.filter(recommendation=instance):
        node.message.soft_delete()


@receiver(message_posted)
def notify_message_created(sender, message, **kwargs):
    project = message.project
    user = message.posted_by

    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    action.send(
        user,
        verb=verbs.Conversation.POST_MESSAGE,
        action_object=message,
        target=project,
    )

    notification = {
        "sender": user,
        "verb": verbs.Conversation.POST_MESSAGE,
        "action_object": message,
        "target": project,
        "annotations": gather_annotations_for_message_notification(message),
    }

    notify_advisors_of_project(project, notification, exclude=user)
    if not project.inactive_since:
        notify_members_of_project(project, notification, exclude=user)


@receiver(message_posted)
def update_project_status(sender, message, **kwargs):
    reactivate_if_necessary(message.project, message.posted_by)
