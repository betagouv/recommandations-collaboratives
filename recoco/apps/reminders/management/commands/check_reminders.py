from datetime import timedelta

from django.core.management.base import BaseCommand

from recoco.apps.reminders.models import Reminder
from recoco.apps.tasks.models import Task


class Command(BaseCommand):
    help = "Check reminders and perform necessary actions"

    def check_reminders_new_reco(self, *args, **kwargs):
        self.stdout.write("Checking reminders NEW_RECO ...")

        for reminder in Reminder.to_send.filter(kind=Reminder.NEW_RECO).select_related(
            "project", "site"
        ):
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

            self.stdout.write(
                f"Reminder {reminder.id}, deadline: {reminder.deadline} / expected: {expected_deadline}"
            )

        self.stdout.write("Reminders check complete.")

    def handle(self, *args, **kwargs):
        self.check_reminders_new_reco(*args, **kwargs)
