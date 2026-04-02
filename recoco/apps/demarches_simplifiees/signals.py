from typing import Any

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DSResource
from .services import load_ds_resource_schema


@receiver(post_save, sender=DSResource)
def trigger_load_ds_resource_schema(
    sender: Any, instance: DSResource, created: bool, **kwargs
):
    if created and settings.DS_AUTOLOAD_SCHEMA:
        load_ds_resource_schema(ds_resource_id=instance.id)
