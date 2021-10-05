import django.dispatch
from actstream import action
from django.dispatch import receiver

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
action_accepted = django.dispatch.Signal()
action_rejected = django.dispatch.Signal()
action_done = django.dispatch.Signal()
action_undone = django.dispatch.Signal()


@receiver(action_accepted)
def log_action_accepted(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(user, verb="a accepté l'action", action_object=task, target=project)


@receiver(action_rejected)
def log_action_rejected(sender, task, project, user, **kwargs):
    if not user.is_staff:
        action.send(user, verb="a refusé l'action", action_object=task, target=project)


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
