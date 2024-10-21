from typing import Any

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from recoco.apps.tasks.models import Task

from .models import DSResource
from .tasks import load_ds_resource_schema, update_or_create_ds_folder


@receiver(post_save, sender=Task)
def trigger_ds_from_task(sender: Any, instance: Task, created: bool, **kwargs):
    if settings.DS_AUTOCREATE_FOLDER:
        update_or_create_ds_folder.delay(recommendation_id=instance.id)


@receiver(post_save, sender=DSResource)
def trigger_load_ds_resource_schema(
    sender: Any, instance: DSResource, created: bool, **kwargs
):
    if created and settings.DS_AUTOLOAD_SCHEMA:
        load_ds_resource_schema.delay(ds_resource_id=instance.id)
