# encoding: utf-8

"""
Command to clean stale notifications of deleted objects

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-09-26 18:57:48 CET
"""

from actstream.models import Action
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clean Stale notifications/actions (deleted objects)"

    def handle(self, *args, **options):
        actions = Action.objects.all()
        for action in actions.all():
            try:
                project_ct = ContentType.objects.get_for_id(
                    id=action.target_content_type_id
                )
            except ContentType.DoesNotExist:
                continue

            klass = project_ct.model_class()

            try:
                klass.objects.get(pk=action.target_object_id)
            except klass.DoesNotExist:
                print(f"[Deleting stale action] {action}")
                action.delete()


# eof
