# encoding: utf-8

"""
Management command to send pending reminder reaching their deadline

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 13:45:27 CEST
"""

import datetime

import django.core.mail
from django.conf import settings
from django.core.management.base import BaseCommand
from urbanvitaliz.apps.communication.api import send_email
from urbanvitaliz.apps.reminders import models
from urbanvitaliz.apps.reminders.api import create_reminder_email


class Command(BaseCommand):
    help = "Send pending email reminders reaching their deadline"

    def handle(self, *args, **options):
        self.send_email_reminders()

    def send_email_reminders(self):
        today = datetime.date.today()
        reminders = models.Mail.to_send.filter(deadline__lte=today)
        for reminder in reminders:
            if reminder.template:
                send_email(
                    reminder.template.name,
                    [{"email": reminder.recipient}],
                    params=reminder.template_params,
                )
            else:
                django.core.mail.send_mail(
                    subject=reminder.subject,
                    message=reminder.text,
                    from_email=settings.EMAIL_FROM,
                    html_message=reminder.html,
                    recipient_list=[reminder.recipient],
                    fail_silently=False,
                )
            reminder.mark_as_sent()

            # Create a new reminder in 6 weeks
            if reminder.template:
                create_reminder_email(
                    recipient=reminder.recipient,
                    template_name=reminder.template.name,
                    template_params=reminder.template_params,
                    related=reminder.related,
                    origin=models.Mail.UNKNOWN,
                    delay=7 * 6,
                )


# eof
