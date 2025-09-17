from typing import Any

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Organization, OrganizationGroup


@receiver(post_save, sender=Organization)
def create_organisation_national_group(
    sender: Any, instance: Organization, created: bool, **kwargs
):
    if not created or instance.has_departments or instance.group is not None:
        return
    with transaction.atomic():
        group, _ = OrganizationGroup.objects.get_or_create(name=instance.name)
        instance.group = group
        instance.save(update_fields=["group"])
