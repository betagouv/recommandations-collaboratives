# encoding: utf-8

"""
Tests for reminders application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 13:17:53 CEST
"""

import datetime

import django.core.mail
import pytest
from django.conf import settings
from django.core.management import call_command
from model_bakery import baker
from urbanvitaliz.apps.communication import models as communication
from urbanvitaliz.apps.projects import models as projects

from . import api, models

########################################################################
# Create reminders
########################################################################


@pytest.mark.django_db
def test_create_mail_reminder_using_provided_information():
    task = baker.make(projects.Task)
    recipient = "test@example.com"
    template = baker.make(communication.EmailTemplate)
    related = task
    delay = 14
    template_params = {"key": "val"}

    api.create_reminder_email(
        recipient=recipient,
        template_name=template.name,
        template_params=template_params,
        related=related,
        delay=delay,
    )

    reminder = models.Mail.to_send.all()[0]

    assert reminder.recipient == recipient
    assert reminder.template == template
    assert reminder.template_params == template_params

    assert reminder.deadline == datetime.date.today() + datetime.timedelta(days=delay)


@pytest.mark.django_db
def test_create_mail_reminder_replace_existing_ones():
    task = baker.make(projects.Task)
    recipient = "test@example.com"
    template = baker.make(communication.EmailTemplate)
    related = task
    delay = 14
    template_params = {"key": "val"}

    baker.make(models.Mail, related=task, recipient=recipient)

    api.create_reminder_email(
        recipient=recipient,
        template_name=template.name,
        template_params=template_params,
        related=related,
        delay=delay,
    )

    assert models.Mail.to_send.count() == 1

    reminder = models.Mail.to_send.all()[0]

    assert reminder.recipient == recipient
    assert reminder.template == template
    assert reminder.template_params == template_params

    assert reminder.deadline == datetime.date.today() + datetime.timedelta(days=delay)


########################################################################
# Sending reminders
########################################################################


@pytest.mark.django_db
def test_command_send_pending_reminder_with_reached_deadline(mocker):
    today = datetime.date.today()
    reminder = baker.make(
        models.Mail,
        recipient="test@example.org",
        subject="[uv] test",
        text="body as text",
        html="<p>body as html</p>",
        deadline=today,
    )

    mocker.patch("django.core.mail.send_mail")

    call_command("sendreminders")

    assert models.Mail.to_send.count() == 0
    updated = models.Mail.sent.all()[0]
    assert updated.id == reminder.id

    django.core.mail.send_mail.assert_called_once_with(
        subject=reminder.subject,
        message=reminder.text,
        html_message=reminder.html,
        from_email=settings.EMAIL_FROM,
        recipient_list=[reminder.recipient],
        fail_silently=False,
    )


@pytest.mark.django_db
def test_command_send_pending_reminder_with_past_deadline(mocker):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    baker.make(
        models.Mail,
        recipient="test@example.org",
        subject="[uv] test",
        text="body as text",
        html="<p>body as html</p>",
        deadline=yesterday,
    )

    mocker.patch("django.core.mail.send_mail")

    call_command("sendreminders")

    assert models.Mail.to_send.count() == 0
    assert models.Mail.sent.count() == 1

    django.core.mail.send_mail.assert_called_once()


@pytest.mark.django_db
def test_command_do_not_send_pending_reminder_with_future_deadline(mocker):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    baker.make(
        models.Mail,
        recipient="test@example.org",
        subject="[uv] test",
        text="body as text",
        html="<p>body as html</p>",
        deadline=tomorrow,
    )

    mocker.patch("django.core.mail.send_mail")

    call_command("sendreminders")

    assert models.Mail.to_send.count() == 1
    assert models.Mail.sent.count() == 0

    django.core.mail.send_mail.assert_not_called()


# eof
