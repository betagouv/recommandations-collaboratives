import django.dispatch
from actstream import action
from django.dispatch import receiver
from notifications.signals import notify

from .utils import get_notification_recipients_for_project

#####
# Projects
#####
project_submitted = django.dispatch.Signal()


@receiver(project_submitted)
def log_project_submitted(sender, project, **kwargs):
    action.send(project, verb="a été déposé")


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
action_visited = django.dispatch.Signal()
action_rejected = django.dispatch.Signal()
action_already_done = django.dispatch.Signal()
action_done = django.dispatch.Signal()
action_undone = django.dispatch.Signal()
action_commented = django.dispatch.Signal()

# TODO refactor arguements as project is know to task -> f(sender, task , user, **kwargs)


@receiver(action_visited)
def log_action_visited(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(user, verb="a visité l'action", action_object=task, target=project)


@receiver(action_rejected)
def log_action_rejected(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(user, verb="a refusé l'action", action_object=task, target=project)


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


# eof
