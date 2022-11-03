# encoding: utf-8

"""
Command to clean stale notifications of deleted objects

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-09-26 18:57:48 CET
"""

from actstream.models import Action
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from notifications.models import Notification
from urbanvitaliz.apps.projects.models import Project


class Command(BaseCommand):
    help = "Clean Stale notifications/actions (deleted objects)"

    def handle(self, *args, **options):
        actions = Action.objects.all()

        # clean actions for deleted objects
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

        # clean notifications for deleted projects
        deleted_projects = Project.objects_deleted.all()
        project_ct = ContentType.objects.get_for_model(Project)

        to_be_deleted = Notification.objects.filter(
            target_content_type=project_ct,
            target_object_id__in=list(deleted_projects.values_list(flat=True)),
        )

        for notification in to_be_deleted:
            print(f"[Deleting stale notification] {notification}")

        to_be_deleted.delete()


# eof
