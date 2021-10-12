# encoding: utf-8

"""
Tests for reminders application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 13:17:53 CEST
"""

import datetime
import pytest

from django.test.client import RequestFactory
from django.conf import settings
from django.core.management import call_command
import django.core.mail

from model_bakery import baker

from urbanvitaliz.apps.projects import models as projects

from . import api
from . import models


########################################################################
# Create reminders
########################################################################


@pytest.mark.django_db
def test_create_mail_reminder_using_provided_information():
    url = "/project/action/0/"
    request = RequestFactory().get(url)
    recipient = "test@example.com"
    subject = "[UV] action reminder"
    template = "reminders/test"
    related = baker.make(projects.Task)
    delay = 14
    extra = {"notes": "some notes."}

    api.create_reminder_email(
        request,
        recipient,
        subject,
        template,
        related=related,
        delay=delay,
        extra_context=extra,
    )

    reminder = models.Mail.to_send.all()[0]

    assert reminder.recipient == recipient
    assert reminder.subject == subject
    assert extra["notes"] in reminder.text
    assert url in reminder.text

    assert reminder.deadline == datetime.date.today() + datetime.timedelta(days=delay)


@pytest.mark.django_db
def test_create_mail_reminder_replace_existing_ones():
    task = baker.make(projects.Task)
    recipient = "test@example.com"
    url = "/project/action/0/"
    request = RequestFactory().get(url)
    subject = "[UV] action reminder"
    template = "reminders/test"
    related = task
    delay = 14
    extra = {"notes": "some notes."}

    baker.make(models.Mail, related=task, recipient=recipient)

    api.create_reminder_email(
        request,
        recipient,
        subject,
        template,
        related=related,
        delay=delay,
        extra_context=extra,
    )

    assert models.Mail.to_send.count() == 1

    reminder = models.Mail.to_send.all()[0]

    assert reminder.recipient == recipient
    assert reminder.subject == subject
    assert extra["notes"] in reminder.text
    assert url in reminder.text

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
