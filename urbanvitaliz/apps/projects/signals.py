import django.dispatch
from actstream import action
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from notifications import models as notifications_models
from notifications.signals import notify

from . import models
from .utils import (
    get_notification_recipients_for_project,
    get_project_moderators,
    get_regional_actors_for_project,
    get_switchtenders_for_project,
)

#####
# Projects
#####
project_submitted = django.dispatch.Signal()
project_validated = django.dispatch.Signal()
project_switchtender_joined = django.dispatch.Signal()


@receiver(project_submitted)
def log_project_submitted(sender, submitter, project, **kwargs):
    action.send(project, verb="a été déposé")


@receiver(project_submitted)
def notify_moderators_project_submitted(sender, submitter, project, **kwargs):
    recipients = get_project_moderators()

    # Notify project moderators
    notify.send(
        sender=submitter,
        recipient=recipients,
        verb="a soumis pour modération le projet",
        action_object=project,
        target=project,
        private=True,
    )


@receiver(project_validated)
def log_project_validated(sender, moderator, project, **kwargs):
    action.send(project, verb="a été validé")

    # Notify regional actors of a new project
    try:
        owner = auth_models.User.objects.get(email=project.email)
    except auth_models.User.DoesNotExist:
        return

    notify.send(
        sender=owner,
        recipient=get_regional_actors_for_project(project),
        verb="a déposé le projet",
        action_object=project,
        target=project,
        private=True,
    )


@receiver(project_switchtender_joined)
def log_project_switchtender_joined(sender, project, **kwargs):
    action.send(
        sender,
        verb="est devenu·e aiguilleur·se sur le projet",
        action_object=project,
        target=project,
    )


@receiver(project_switchtender_joined)
def notify_project_switchtender_joined(sender, project, **kwargs):
    recipients = get_regional_actors_for_project(project, allow_national=True)

    # Notify regional actors
    notify.send(
        sender=sender,
        recipient=recipients,
        verb="est devenu·e aiguilleur·se sur le projet",
        action_object=project,
        target=project,
        private=True,
    )


#####
# Reminders
#####
reminder_created = django.dispatch.Signal()


@receiver(reminder_created)
def log_reminder_created(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(
            user,
            verb="a créé un rappel sur l'action",
            action_object=task,
            target=project,
        )


######
# Actions
#####
action_created = django.dispatch.Signal()
action_visited = django.dispatch.Signal()
action_not_interested = django.dispatch.Signal()
action_blocked = django.dispatch.Signal()
action_inprogress = django.dispatch.Signal()
action_already_done = django.dispatch.Signal()
action_done = django.dispatch.Signal()
action_undone = django.dispatch.Signal()
action_commented = django.dispatch.Signal()

# TODO refactor arguements as project is know to task -> f(sender, task , user, **kwargs)


@receiver(action_created)
def notify_action_created(sender, task, project, user, **kwargs):
    recipients = get_notification_recipients_for_project(project).exclude(id=user.id)

    notify.send(
        sender=user,
        recipient=recipients,
        verb="a recommandé l'action",
        action_object=task,
        target=project,
        private=True,
    )


@receiver(action_visited)
def log_action_visited(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(user, verb="a visité l'action", action_object=task, target=project)


@receiver(action_not_interested)
def log_action_not_interested(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(
            user,
            verb="n'est pas intéressé·e l'action",
            action_object=task,
            target=project,
        )


@receiver(action_blocked)
def log_action_blocked(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(
            user,
            verb="est bloqué sur l'action",
            action_object=task,
            target=project,
        )


@receiver(action_already_done)
def log_action_already_done(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(
            user, verb="a déjà fait l'action", action_object=task, target=project
        )


@receiver(action_done)
def log_action_done(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(user, verb="a terminé l'action", action_object=task, target=project)


@receiver(action_inprogress)
def log_action_inprogress(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(
            user,
            verb="travaille sur l'action",
            action_object=task,
            target=project,
        )


@receiver(action_undone)
def log_action_undone(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(
            user, verb="a redémarré l'action", action_object=task, target=project
        )


@receiver(action_commented)
def log_action_commented(sender, task, project, user, **kwargs):
    action.send(user, verb="a commenté l'action", action_object=task, target=project)


@receiver(action_commented)
def notify_action_commented(sender, task, project, user, **kwargs):
    recipients = get_notification_recipients_for_project(project).exclude(id=user.id)

    notify.send(
        sender=user,
        recipient=recipients,
        verb="a commenté l'action",
        action_object=sender,
        target=project,
        private=True,
    )


# In case of deletion
@receiver(
    pre_delete, sender=models.Project, dispatch_uid="project_delete_notifications"
)
def delete_notifications_on_project_delete(sender, instance, **kwargs):
    project_ct = ContentType.objects.get_for_model(instance)
    notifications_models.Notification.objects.filter(
        target_content_type=project_ct.pk, target_object_id=instance.pk
    ).delete()


@receiver(pre_delete, sender=models.Task, dispatch_uid="task_delete_notifications")
def delete_notifications_on_task_delete(sender, instance, **kwargs):
    task_ct = ContentType.objects.get_for_model(instance)
    notifications_models.Notification.objects.filter(
        action_object_content_type_id=task_ct.pk, action_object_object_id=instance.pk
    ).delete()


######
# Notes
#####
note_created = django.dispatch.Signal()


@receiver(note_created)
def notify_note_created(sender, note, project, user, **kwargs):
    if note.public is False:
        recipients = get_switchtenders_for_project(project).exclude(id=user.id)
        action.send(
            user, verb="a rédigé une note interne", action_object=note, target=project
        )
    else:
        recipients = get_notification_recipients_for_project(project).exclude(
            id=user.id
        )

    notify.send(
        sender=user,
        recipient=recipients,
        verb="a créé une note de suivi",
        action_object=note,
        target=project,
        private=True,
    )


# eof
