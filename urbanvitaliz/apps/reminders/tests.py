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
from model_bakery import baker
from django.contrib.auth import models as auth_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.projects.utils import assign_collaborator
from urbanvitaliz.apps.tasks import models as tasks_models

from . import api, models

########################################################################
# Create reminders
########################################################################


@pytest.mark.django_db
def test_make_reminder(request):
    current_site = get_current_site(request)

    project = baker.make(projects_models.Project, sites=[current_site])
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

    project = baker.make(projects_models.Project, sites=[current_site])
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

    project = baker.make(projects_models.Project, sites=[current_site])
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

    project = baker.make(projects_models.Project, sites=[current_site])
    kind = models.Reminder.NEW_RECO
    deadline = datetime.date.today()

    baker.make(
        models.Reminder,
        project=project,
        deadline=deadline - datetime.timedelta(days=6),
        kind=kind,
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
def test_update_reminder_doesnt_update_sent_one(request):
    current_site = get_current_site(request)

    project = baker.make(projects_models.Project, sites=[current_site])
    kind = models.Reminder.NEW_RECO
    deadline = datetime.date.today()

    baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        kind=kind,
        deadline=deadline - datetime.timedelta(days=6),
    )

    baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        kind=kind,
        deadline=deadline - datetime.timedelta(days=6),
        sent_on=timezone.now(),
    )

    api.make_or_update_reminder(
        site=current_site, project=project, deadline=deadline, kind=kind
    )

    sent_reminder = models.Reminder.on_site_sent.first()

    assert sent_reminder.deadline <= deadline
    assert sent_reminder.sent_on is not None

    assert models.Reminder.on_site_to_send.count() == 1
    assert models.Reminder.on_site_sent.count() == 1


@pytest.mark.django_db
def test_update_reminder_doesnt_update_another_kind(request):
    current_site = get_current_site(request)

    project = baker.make(projects_models.Project, sites=[current_site])
    kind = models.Reminder.NEW_RECO
    deadline = datetime.date.today()

    other_deadline = deadline - datetime.timedelta(days=6)
    other_reminder = baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        kind=models.Reminder.WHATS_UP,
        deadline=other_deadline,
    )

    target_reminder = baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        kind=kind,
        deadline=deadline - datetime.timedelta(days=10),
    )

    api.make_or_update_reminder(
        site=current_site, project=project, deadline=deadline, kind=kind
    )

    target_reminder.refresh_from_db()
    other_reminder.refresh_from_db()

    assert target_reminder.deadline == deadline
    assert target_reminder.kind == kind

    assert other_reminder.deadline == other_deadline
    assert other_reminder.kind == models.Reminder.WHATS_UP

    assert models.Reminder.on_site_to_send.count() == 2


########################################################################
# New reco reminders
########################################################################
@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_with_no_task(request):
    current_site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[current_site])

    api.make_or_update_new_recommendations_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 0


@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_with_unpublished_task(request):
    current_site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[current_site])
    baker.make(
        tasks_models.Task,
        project=project,
        public=False,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

    api.make_or_update_new_recommendations_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 0


@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_with_task_in_uninteresting_states(request):
    current_site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[current_site])
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.DONE,
    )
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.NOT_INTERESTED,
    )

    api.make_or_update_new_recommendations_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 0


@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_with_existing_reminder(request):
    current_site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[current_site])

    reminder = baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        kind=models.Reminder.NEW_RECO,
        deadline=timezone.localdate() - datetime.timedelta(days=6),
    )

    task = baker.make(
        tasks_models.Task,
        created_on=timezone.now(),
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

    assert reminder.deadline < task.created_on.date()

    api.make_or_update_new_recommendations_reminder(current_site, project)

    reminder.refresh_from_db()

    assert reminder.deadline >= task.created_on.date()

    assert models.Reminder.on_site_to_send.count() == 1


@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_with_tasks_uses_the_most_recent(request):
    current_site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[current_site])
    baker.make(
        tasks_models.Task,
        created_on=timezone.now() - datetime.timedelta(days=200),
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )
    recent_task = baker.make(
        tasks_models.Task,
        created_on=timezone.now(),
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

    api.make_or_update_new_recommendations_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 1
    reminder = models.Reminder.on_site.first()
    assert reminder.deadline >= recent_task.created_on.date()


@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_with_task_on_site(request):
    current_site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[current_site])
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
    )

    api.make_or_update_new_recommendations_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 1


@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_with_task_off_site(request):
    current_site = get_current_site(request)
    other_site = baker.make(sites_models.Site)
    project = baker.make(projects_models.Project, sites=[current_site])
    baker.make(
        tasks_models.Task,
        public=True,
        project=project,
        site=other_site,
    )

    api.make_or_update_new_recommendations_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 0


########################################################################
# Getting reminders
########################################################################
@pytest.mark.django_db
def test_reminder_is_due(request):
    current_site = get_current_site(request)
    today = timezone.localdate()
    user = baker.make(auth_models.User)
    project = baker.make(projects_models.Project, sites=[current_site])
    assign_collaborator(user, project, is_owner=True)

    kind = models.Reminder.NEW_RECO

    baker.make(
        models.Reminder,
        deadline=today,
        project=project,
        site=current_site,
        kind=kind,
    )

    reminder = api.get_due_reminder_for_project(current_site, project, kind=kind)

    assert reminder


@pytest.mark.django_db
def test_reminder_is_not_due(request, mocker):
    current_site = get_current_site(request)

    tomorrow = timezone.localdate() + datetime.timedelta(days=1)
    project = baker.make(projects_models.Project, sites=[current_site])

    kind = models.Reminder.NEW_RECO

    baker.make(
        models.Reminder,
        deadline=tomorrow,
        project=project,
        site=current_site,
        kind=kind,
    )

    reminder = api.get_due_reminder_for_project(current_site, project, kind=kind)

    assert reminder is None


@pytest.mark.django_db
def test_reminder_already_sent(request, mocker):
    current_site = get_current_site(request)

    today = timezone.localdate()
    project = baker.make(projects_models.Project, sites=[current_site])

    kind = models.Reminder.NEW_RECO

    baker.make(
        models.Reminder,
        deadline=today,
        project=project,
        site=current_site,
        kind=kind,
        sent_on=today,
    )

    reminder = api.get_due_reminder_for_project(current_site, project, kind=kind)

    assert reminder is None


@pytest.mark.django_db
def test_due_reminder_honors_kind_argumnent(request, mocker):
    current_site = get_current_site(request)

    today = timezone.localdate()
    project = baker.make(projects_models.Project, sites=[current_site])

    baker.make(
        models.Reminder,
        deadline=today,
        project=project,
        site=current_site,
        kind=models.Reminder.NEW_RECO,
    )

    reminder = api.get_due_reminder_for_project(
        current_site, project, kind=models.Reminder.WHATS_UP
    )

    assert reminder is None


@pytest.mark.django_db
def test_due_reminder_honors_current_site(request, mocker):
    current_site = get_current_site(request)
    other_site = baker.make(sites_models.Site)

    today = timezone.localdate()
    project = baker.make(projects_models.Project, sites=[current_site])

    kind = models.Reminder.NEW_RECO

    baker.make(
        models.Reminder,
        deadline=today,
        project=project,
        site=other_site,
        kind=kind,
    )

    reminder = api.get_due_reminder_for_project(current_site, project, kind=kind)

    assert reminder is None


#################################################################
# Getting Recommendation Reminders
#################################################################
@pytest.mark.django_db
def test_due_new_recommendations_reminder_honors_task_status(request, mocker):
    current_site = get_current_site(request)

    today = timezone.localdate()
    project = baker.make(projects_models.Project, sites=[current_site])

    baker.make(
        tasks_models.Task,
        created_on=timezone.now(),
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.DONE,
    )

    kind = models.Reminder.NEW_RECO

    baker.make(
        models.Reminder,
        deadline=today,
        project=project,
        site=current_site,
        kind=kind,
    )

    reminder = api.get_due_new_recommendations_reminder_for_project(
        current_site, project
    )

    assert reminder is None


@pytest.mark.django_db
def test_due_new_recommendations_reminder_is_deleted_if_no_task(request, mocker):
    current_site = get_current_site(request)

    today = timezone.localdate()
    project = baker.make(projects_models.Project, sites=[current_site])

    baker.make(
        models.Reminder,
        deadline=today,
        project=project,
        site=current_site,
        kind=models.Reminder.NEW_RECO,
    )

    reminder = api.get_due_new_recommendations_reminder_for_project(
        current_site, project
    )

    assert reminder is None


########################################################################
# Sending reminders
########################################################################

# FIXME pourquoi ces tests ne sont pas dans communication avec la commande
# senddigest ou la commande senddigest dans l'application courante ?


# eof
