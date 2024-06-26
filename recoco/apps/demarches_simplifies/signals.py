from django.db.models.signals import post_save
from django.dispatch import receiver

from recoco.apps.projects.models import Project

from .tasks import call_ds_api_preremplir


@receiver(post_save, sender=Project)
def trigger_ds_from_project(sender, instance, created, **kwargs):
    # TODO: check if project is in a state that can be sent to DS
    call_ds_api_preremplir(project_id=instance.id)
