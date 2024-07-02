from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from recoco.apps.projects.models import Project
from recoco.apps.survey.models import Answer

from .models import DSResource
from .tasks import load_ds_resource_schema, update_or_create_ds_action


def _is_project_ready_for_ds(project: Project) -> bool:
    # TODO: check if project is ready for receiving a DETR recommendation
    return True


@receiver(post_save, sender=Project)
def trigger_ds_from_project(sender: Any, instance: Project, created: bool, **kwargs):
    if _is_project_ready_for_ds(instance):
        update_or_create_ds_action.delay(project_id=instance.id)


@receiver(post_save, sender=Answer)
def trigger_ds_from_answer(sender: Any, instance: Answer, created: bool, **kwargs):
    project = instance.session.project
    if _is_project_ready_for_ds(project):
        update_or_create_ds_action.delay(project_id=project.id)


@receiver(post_save, sender=DSResource)
def trigger_load_ds_resource_schema(
    sender: Any, instance: DSResource, created: bool, **kwargs
):
    if created:
        load_ds_resource_schema(ds_resource_id=instance.id)
