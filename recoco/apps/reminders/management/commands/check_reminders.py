from datetime import timedelta

from django.core.management.base import BaseCommand

from recoco.apps.reminders.api import make_or_update_new_recommendations_reminder
from recoco.apps.reminders.models import Reminder
from recoco.apps.tasks.models import Task


class Command(BaseCommand):
    help = "Check reminders and perform necessary actions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Fix the reminders with incorrect deadlines",
        )

    def _get_reminders_new_reco_to_update(self) -> list[int]:
        reminders_to_update: list[int] = []

        for reminder in Reminder.to_send.select_related("project", "site"):
            last_task = (
                reminder.project.tasks.filter(status__in=Task.OPEN_STATUSES)
                .filter(site_id=reminder.site_id)
                .exclude(public=False)
                .order_by("-created_on")
                .first()
            )
            if not last_task:
                continue

            expected_deadline = (last_task.created_on + timedelta(days=6 * 7)).date()
            if reminder.deadline == expected_deadline:
                continue

            reminders_to_update.append(reminder.id)
            self.stdout.write(
                f"Reminder {reminder.id}, deadline is: {reminder.deadline}, but expected is: {expected_deadline}"
            )

        return reminders_to_update

    def check_reminders_new_reco(self, *args, **kwargs):
        self.stdout.write("Checking reminders NEW_RECO ...")

        reminders_to_update: list[int] = self._get_reminders_new_reco_to_update()

        if kwargs["fix"] and len(reminders_to_update):
            for reminder in Reminder.to_send.filter(
                id__in=reminders_to_update, kind=Reminder.NEW_RECO
            ).select_related("project", "site"):
                self.stdout.write(
                    f"Fixing reminder {reminder.id}({reminder.kind}) deadline."
                )
                make_or_update_new_recommendations_reminder(
                    site=reminder.site, project=reminder.project
                )

        self.stdout.write("Reminders check complete.")

    def handle(self, *args, **kwargs):
        self.check_reminders_new_reco(*args, **kwargs)
