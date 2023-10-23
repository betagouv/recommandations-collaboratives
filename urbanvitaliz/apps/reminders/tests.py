# encoding: utf-8

"""
Tests for reminders application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 13:17:53 CEST
"""

import datetime

import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites import models as sites_models
from django.utils import timezone
from django.core.management import call_command
from django.test import override_settings
from model_bakery import baker
from urbanvitaliz.apps.communication import api as communication_api
from urbanvitaliz.apps.projects import models as project_models
from urbanvitaliz.apps.tasks import models as tasks

from . import api, models

########################################################################
# Create reminders
########################################################################


@pytest.mark.django_db
def test_make_reminder(request):
    current_site = get_current_site(request)

    project = baker.make(project_models.Project, sites=[current_site])
    kind = models.Reminder.NEW_RECO
    deadline = datetime.date.today()

    api.make_or_update_reminder(
        site=current_site, project=project, deadline=deadline, kind=kind
    )

    reminder = models.Reminder.on_site_to_send.first()

    assert reminder.deadline == deadline
    assert reminder.project == project
    assert reminder.kind == kind

    assert models.Reminder.on_site_to_send.count() == 1


@pytest.mark.django_db
def test_make_reminder_on_wrong_site(request):
    current_site = get_current_site(request)

    project = baker.make(project_models.Project, sites=[current_site])
    other_site = baker.make(sites_models.Site)
    kind = models.Reminder.NEW_RECO
    deadline = datetime.date.today()

    api.make_or_update_reminder(
        site=other_site, project=project, deadline=deadline, kind=kind
    )

    models.Reminder.on_site_to_send.first()

    assert models.Reminder.on_site_to_send.count() == 0


@pytest.mark.django_db
def test_make_reminder_with_past_deadline(request):
    current_site = get_current_site(request)

    project = baker.make(project_models.Project, sites=[current_site])
    other_site = baker.make(sites_models.Site)
    kind = models.Reminder.NEW_RECO
    deadline = datetime.date.today() - datetime.timedelta(days=1)

    api.make_or_update_reminder(
        site=other_site, project=project, deadline=deadline, kind=kind
    )

    models.Reminder.on_site_to_send.first()

    assert models.Reminder.on_site_to_send.count() == 0


@pytest.mark.django_db
def test_update_reminder(request):
    current_site = get_current_site(request)

    project = baker.make(project_models.Project, sites=[current_site])
    kind = models.Reminder.NEW_RECO
    deadline = datetime.date.today()

    baker.make(
        models.Reminder, project=project, deadline=deadline - datetime.timedelta(days=6)
    )

    api.make_or_update_reminder(
        site=current_site, project=project, deadline=deadline, kind=kind
    )

    reminder = models.Reminder.on_site_to_send.first()

    assert reminder.deadline == deadline
    assert reminder.project == project
    assert reminder.kind == kind

    assert models.Reminder.on_site_to_send.count() == 1


@pytest.mark.django_db
def test_update_reminder_dont_update_sent_one(request):
    current_site = get_current_site(request)

    project = baker.make(project_models.Project, sites=[current_site])
    kind = models.Reminder.NEW_RECO
    deadline = datetime.date.today()

    baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        deadline=deadline - datetime.timedelta(days=6),
    )

    baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        deadline=deadline - datetime.timedelta(days=6),
        sent_on=timezone.now(),
    )

    api.make_or_update_reminder(
        site=current_site, project=project, deadline=deadline, kind=kind
    )

    reminder = models.Reminder.on_site_to_send.first()

    assert reminder.deadline == deadline
    assert reminder.project == project
    assert reminder.kind == kind

    assert models.Reminder.on_site_to_send.count() == 1
    assert models.Reminder.on_site_sent.count() == 1


########################################################################
# Sending reminders
########################################################################

# FIXME pourquoi ces tests ne sont pas dans communication avec la commande
# senddigest ou la commande senddigest dans l'application courante ?


@pytest.mark.django_db
@override_settings(BREVO_FORCE_DEBUG=True)
def test_command_send_pending_reminder_with_reached_deadline(request, mocker):
    current_site = get_current_site(request)
    today = datetime.date.today()
    task = baker.make(tasks.Task, site=current_site)
    reminder = baker.make(models.Reminder, deadline=today, related=task)

    mocker.patch("urbanvitaliz.apps.communication.api.send_debug_email")

    call_command("senddigests")

    assert models.Reminder.to_send.count() == 1
    new = models.Reminder.to_send.first()
    assert new.deadline == today + datetime.timedelta(weeks=6)
    updated = models.Reminder.sent.first()
    assert updated.id == reminder.id


@pytest.mark.django_db
@override_settings(BREVO_FORCE_DEBUG=True)
def test_command_send_pending_task_reminder_with_past_deadline(request, mocker):
    current_site = get_current_site(request)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    task = baker.make(tasks.Task, site=current_site)
    baker.make(models.Reminder, deadline=yesterday, related=task)

    call_command("senddigests")

    assert models.Reminder.to_send.count() == 1
    assert models.Reminder.sent.count() == 1


@pytest.mark.django_db
@override_settings(BREVO_FORCE_DEBUG=True)
def test_command_do_not_send_pending_reminder_with_future_deadline(mocker):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    baker.make(
        models.Reminder,
        deadline=tomorrow,
    )

    mocker.patch("urbanvitaliz.apps.communication.api.send_debug_email")

    call_command("senddigests")

    assert models.Reminder.to_send.count() == 1
    assert models.Reminder.sent.count() == 0

    communication_api.send_debug_email.assert_not_called()


# eof
