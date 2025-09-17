from django.dispatch import receiver

from recoco.apps.tasks.signals import action_created

from .utils import post_public_message_with_recommendation


@receiver(action_created)
def make_message_on_action_creation(sender, task, project, user, **kwargs):
    if task.public is False:
        return

    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    post_public_message_with_recommendation(recommendation=task)
