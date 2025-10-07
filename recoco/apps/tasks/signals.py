import datetime

import django.dispatch
from actstream import action
from actstream.models import action_object_stream
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from notifications import models as notifications_models

from recoco import verbs
from recoco.apps.projects.utils import (
    notify_advisors_of_project,
    notify_members_of_project,
)
from recoco.utils import is_staff_for_site

from . import models

########################################################################
# Actions
########################################################################


action_created = django.dispatch.Signal()
action_visited = django.dispatch.Signal()
action_not_interested = django.dispatch.Signal()
action_blocked = django.dispatch.Signal()
action_inprogress = django.dispatch.Signal()
action_already_done = django.dispatch.Signal()
action_done = django.dispatch.Signal()
action_undone = django.dispatch.Signal()
action_commented = django.dispatch.Signal()


@receiver(action_created)
def log_action_created(sender, task, project, user, **kwargs):
    if task.public is False:
        action.send(
            user,
            verb=verbs.Recommendation.DRAFTED,
            action_object=task,
            target=project,
            public=False,
        )
    else:
        action.send(
            user, verb=verbs.Recommendation.CREATED, action_object=task, target=project
        )


@receiver(action_created)
def update_creation_date_on_action_created(sender, task, project, user, **kwargs):
    if task.public is False:
        return

    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    task.created_on = timezone.now()
    task.save()


@receiver(action_visited)
def log_action_visited(sender, task, project, user, **kwargs):
    if not is_staff_for_site(user):
        action.send(
            user,
            verb=verbs.Recommendation.SEEN,
            action_object=task,
            target=project,
        )


@receiver(action_not_interested)
def log_action_not_interested(sender, task, project, user, **kwargs):
    # FIXME to be moved to not applicable
    if not is_staff_for_site(user):
        action.send(
            user,
            verb=verbs.Recommendation.NOT_INTERESTED,
            action_object=task,
            target=project,
        )


@receiver(action_blocked)
def log_action_blocked(sender, task, project, user, **kwargs):
    if not is_staff_for_site(user):
        action.send(
            user,
            verb=verbs.Recommendation.STANDBY,
            action_object=task,
            target=project,
        )


@receiver(action_already_done)
def log_action_already_done(sender, task, project, user, **kwargs):
    if not is_staff_for_site(user):
        action.send(
            user,
            verb=verbs.Recommendation.ALREADY_DONE,
            action_object=task,
            target=project,
        )


@receiver(action_done)
def log_action_done(sender, task, project, user, **kwargs):
    if not is_staff_for_site(user):
        action.send(
            user,
            verb=verbs.Recommendation.DONE,
            action_object=task,
            target=project,
        )


@receiver(action_inprogress)
def log_action_inprogress(sender, task, project, user, **kwargs):
    if not is_staff_for_site(user):
        action.send(
            user,
            verb=verbs.Recommendation.IN_PROGRESS,
            action_object=task,
            target=project,
        )


# FIXME to convert to action_resume ?
@receiver(action_undone)
def log_action_undone(sender, task, project, user, **kwargs):
    if not is_staff_for_site(user):
        action.send(
            user, verb=verbs.Recommendation.RESUMED, action_object=task, target=project
        )


@receiver(action_commented)
def log_action_commented(sender, task, project, user, **kwargs):
    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    action.send(
        user,
        verb=verbs.Recommendation.COMMENTED,
        action_object=task,
        target=project,
    )


@receiver(action_commented)
def notify_action_commented(sender, task, project, user, **kwargs):
    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    notification = {
        "sender": user,
        "verb": verbs.Recommendation.COMMENTED,
        "action_object": sender,
        "target": project,
    }

    notify_advisors_of_project(project, notification, exclude=user)
    if not project.inactive_since:
        notify_members_of_project(project, notification, exclude=user)


def delete_task_history(
    task,
    suppress_notifications=True,
    suppress_actions=True,
    after=None,
):
    """Remove all logging history and notification if a task is deleted"""
    task_ct = ContentType.objects.get_for_model(task)
    notifications = notifications_models.Notification.objects.filter(
        action_object_content_type_id=task_ct.pk, action_object_object_id=task.pk
    )
    actions = action_object_stream(task)

    if after:
        notifications = notifications.filter(timestamp__gte=after)
        actions = actions.filter(timestamp__gte=after)

    if suppress_notifications:
        notifications.delete()

    if suppress_actions:
        actions.delete()


@receiver(pre_save, sender=models.Task, dispatch_uid="task_soft_delete_notifications")
def delete_notifications_on_soft_task_delete(sender, instance, **kwargs):
    if instance.deleted is None:
        return
    delete_task_history(instance)


@receiver(
    pre_save,
    sender=models.Task,
    dispatch_uid="task_cancel_publishing_deletes_notifications",
)
def delete_notifications_on_cancel_publishing(sender, instance, **kwargs):
    if instance.pk and instance.public is False:
        delete_task_history(
            instance,
            suppress_actions=False,
            after=timezone.now() - datetime.timedelta(minutes=30),
        )


@receiver(pre_delete, sender=models.Task, dispatch_uid="task_hard_delete_notifications")
def delete_notifications_on_hard_task_delete(sender, instance, **kwargs):
    delete_task_history(instance)


######################################################################################
# TaskFollowup / Task Status update
######################################################################################
@receiver(
    post_save, sender=models.TaskFollowup, dispatch_uid="taskfollowup_set_task_status"
)
def set_task_status_when_followup_is_issued(sender, instance, created, **kwargs):
    if not created:  # We don't want to notify about updates
        return

    project = instance.task.project

    task_status_signals = {
        models.Task.INPROGRESS: action_inprogress,
        models.Task.DONE: action_done,
        models.Task.ALREADY_DONE: action_already_done,
        models.Task.NOT_INTERESTED: action_not_interested,
        models.Task.BLOCKED: action_blocked,
    }

    muted = (project.project_sites.current().status == "DRAFT") or project.muted

    # Notify about status change
    if instance.status is not None and instance.status != instance.task.status:
        instance.task.status = instance.status
        instance.task.save()

        if not muted:
            if instance.status in task_status_signals.keys():
                signal = task_status_signals[instance.status]
                signal.send(
                    sender=models.TaskFollowup,
                    task=instance.task,
                    project=instance.task.project,
                    user=instance.who,
                )

    if not muted and instance.comment:
        # Notify about comment
        action_commented.send(
            sender=instance,
            task=instance.task,
            project=instance.task.project,
            user=instance.who,
        )


# eof
