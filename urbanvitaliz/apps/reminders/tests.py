# encoding: utf-8

"""
Tests for reminders application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 13:17:53 CEST
"""

import datetime

import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import models as auth_models
from django.core.management import call_command
from django.test import override_settings
from model_bakery import baker
from urbanvitaliz.apps.communication import api as communication_api
from urbanvitaliz.apps.projects import models as projects

from . import api, models

########################################################################
# Create reminders
########################################################################


@pytest.mark.django_db
def test_create_mail_reminder_using_provided_information():
    task = baker.make(projects.Task)
    recipient = "test@example.com"
    related = task
    delay = 14

    api.create_reminder_email(
        recipient=recipient,
        related=related,
        delay=delay,
    )

    reminder = models.Reminder.to_send.all()[0]

    assert reminder.recipient == recipient
    assert reminder.deadline == datetime.date.today() + datetime.timedelta(days=delay)


@pytest.mark.django_db
def test_create_mail_reminder_replace_existing_ones():
    task = baker.make(projects.Task)
    recipient = "test@example.com"
    related = task
    delay = 14

    baker.make(models.Reminder, related=task, recipient=recipient)

    api.create_reminder_email(
        recipient=recipient,
        related=related,
        delay=delay,
    )

    assert models.Reminder.to_send.count() == 1

    reminder = models.Reminder.to_send.all()[0]

    assert reminder.recipient == recipient
    assert reminder.deadline == datetime.date.today() + datetime.timedelta(days=delay)


########################################################################
# Sending reminders
########################################################################


@pytest.mark.django_db
@override_settings(SENDINBLUE_FORCE_DEBUG=True)
def test_command_send_pending_reminder_with_reached_deadline(request, mocker):
    current_site = get_current_site(request)
    today = datetime.date.today()
    user = baker.make(auth_models.User, email="test@example.org")
    task = baker.make(projects.Task, site=current_site)
    reminder = baker.make(
        models.Reminder, recipient=user.email, deadline=today, related=task
    )

    mocker.patch("urbanvitaliz.apps.communication.api.send_debug_email")

    call_command("senddigests")

    assert models.Reminder.to_send.count() == 1
    new = models.Reminder.to_send.first()
    assert new.deadline == today + datetime.timedelta(weeks=6)
    updated = models.Reminder.sent.first()
    assert updated.id == reminder.id


@pytest.mark.django_db
@override_settings(SENDINBLUE_FORCE_DEBUG=True)
def test_command_send_pending_task_reminder_with_past_deadline(request, mocker):
    current_site = get_current_site(request)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    user = baker.make(auth_models.User, email="test@example.org")
    task = baker.make(projects.Task, site=current_site)
    baker.make(models.Reminder, recipient=user.email, deadline=yesterday, related=task)

    call_command("senddigests")

    assert models.Reminder.to_send.count() == 1
    assert models.Reminder.sent.count() == 1


@pytest.mark.django_db
@override_settings(SENDINBLUE_FORCE_DEBUG=True)
def test_command_do_not_send_pending_reminder_with_future_deadline(mocker):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    baker.make(
        models.Reminder,
        recipient="test@example.org",
        deadline=tomorrow,
    )

    mocker.patch("urbanvitaliz.apps.communication.api.send_debug_email")

    call_command("senddigests")

    assert models.Reminder.to_send.count() == 1
    assert models.Reminder.sent.count() == 0

    communication_api.send_debug_email.assert_not_called()


# eof
