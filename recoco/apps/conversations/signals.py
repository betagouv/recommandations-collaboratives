import django.dispatch
from django.dispatch import receiver

from recoco.apps.tasks.signals import action_created

from ..projects.utils import reactivate_if_necessary
from .utils import post_public_message_with_recommendation

message_sent = django.dispatch.Signal()


@receiver(action_created)
def make_message_on_action_creation(sender, task, project, user, **kwargs):
    """Post a public message with the recommendation attached. This workaround is needed
    as long as we don't natively support recommendation handling from the chat interface."""
    if task.public is False:
        return

    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    post_public_message_with_recommendation(recommendation=task)


@receiver(message_sent)
def update_project_status(sender, instance, **kwargs):
    reactivate_if_necessary(instance.project, instance.posted_by)
