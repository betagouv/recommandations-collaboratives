import django.dispatch
from actstream import action
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

#####
# Projects
#####
project_submitted = django.dispatch.Signal()


@receiver(project_submitted)
def log_project_submitted(sender, project, user, **kwargs):
    action.send(user, verb="a déposé le projet", action_object=project)


######
# Actions
#####
action_accepted = django.dispatch.Signal()
action_rejected = django.dispatch.Signal()
action_done = django.dispatch.Signal()
action_undone = django.dispatch.Signal()


@receiver(action_accepted)
def log_action_accepted(sender, task, project, user, **kwargs):
    action.send(user, verb="a accepté l'action", action_object=task, target=project)


@receiver(action_rejected)
def log_action_rejected(sender, task, project, user, **kwargs):
    action.send(user, verb="a refusé l'action", action_object=task, target=project)


@receiver(action_done)
def log_action_done(sender, task, project, user, **kwargs):
    action.send(user, verb="a terminé l'action", action_object=task, target=project)


@receiver(action_undone)
def log_action_undone(sender, task, project, user, **kwargs):
    action.send(user, verb="a redémarré l'action", action_object=task, target=project)
