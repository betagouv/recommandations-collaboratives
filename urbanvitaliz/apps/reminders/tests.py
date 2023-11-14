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
from urbanvitaliz.apps.home import models as home_models

from . import api, models

########################################################################
# Create reminders
########################################################################


@pytest.mark.django_db
def test_make_reminder(request):
    current_site = get_current_site(request)

    project = baker.make(projects_models.Project, sites=[current_site])
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

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
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

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
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

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
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )
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
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

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
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

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
def test_make_or_update_new_reco_reminder_with_task_in_closed_states(request):
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


@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_postpones_reminder_if_new_task(request):
    current_site = get_current_site(request)
    yesterday = timezone.localdate() - datetime.timedelta(days=1)
    user = baker.make(auth_models.User)

    project = baker.make(projects_models.Project, sites=[current_site])
    assign_collaborator(user, project, is_owner=True)

    task = baker.make(
        tasks_models.Task,
        project=project,
        site=current_site,
        status=tasks_models.Task.PROPOSED,
        created_on=timezone.now(),
        public=True,
    )

    reminder = baker.make(
        models.Reminder,
        deadline=yesterday,
        project=project,
        site=current_site,
        kind=models.Reminder.NEW_RECO,
    )

    api.make_or_update_new_recommendations_reminder(
        current_site, project, interval_in_days=7 * 6
    )

    reminder.refresh_from_db()
    assert (
        reminder.deadline == (task.created_on + datetime.timedelta(days=7 * 6)).date()
    )


@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_not_scheduled_if_tasks_too_old(request):
    current_site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[current_site])
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
        created_on=timezone.localdate() - datetime.timedelta(days=70),
    )

    api.make_or_update_new_recommendations_reminder(current_site, project)

    assert models.Reminder.on_site.count() == 0


@pytest.mark.django_db
def test_make_or_update_new_recommendations_reminder_is_deleted_if_no_task(
    request, mocker
):
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

    assert models.Reminder.on_site.count() == 1
    reminder = api.make_or_update_new_recommendations_reminder(current_site, project)

    assert reminder is None
    assert models.Reminder.on_site.count() == 0


@pytest.mark.django_db
def test_make_or_update_new_reco_reminder_with_sent_reminder_honors_interval(
    request,
):
    """Make sure we do not reschedule a reminder the day after the one sent"""
    current_site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration, site=current_site, reminder_interval=6 * 7
    )
    project = baker.make(projects_models.Project, sites=[current_site])

    reminder = baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        kind=models.Reminder.NEW_RECO,
        sent_on=timezone.localdate() - datetime.timedelta(days=2),
        deadline=timezone.localdate() - datetime.timedelta(days=6),
    )

    baker.make(
        tasks_models.Task,
        created_on=timezone.now() - datetime.timedelta(days=10),
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

    api.make_or_update_new_recommendations_reminder(current_site, project)

    reminder.refresh_from_db()

    assert models.Reminder.on_site_to_send.count() == 1
    assert models.Reminder.on_site_sent.count() == 1

    next_reminder = models.Reminder.on_site_to_send.first()

    assert (
        next_reminder.deadline
        == (
            reminder.sent_on
            + datetime.timedelta(days=current_site.configuration.reminder_interval)
        ).date()
    )


########################################################################
# What's up reminders
########################################################################
@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_with_no_task(request):
    current_site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now(),
    )

    api.make_or_update_whatsup_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 0


@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_with_unpublished_task(request):
    current_site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now(),
    )
    baker.make(
        tasks_models.Task,
        project=project,
        public=False,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

    api.make_or_update_whatsup_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 0


@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_with_task_in_uninteresting_states(request):
    current_site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now(),
    )
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

    api.make_or_update_whatsup_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 0


@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_with_existing_reminder(request):
    current_site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now(),
    )

    reminder = baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        kind=models.Reminder.WHATS_UP,
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

    api.make_or_update_whatsup_reminder(current_site, project)

    reminder.refresh_from_db()

    assert reminder.deadline >= task.created_on.date()

    assert models.Reminder.on_site_to_send.count() == 1


@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_with_tasks_uses_the_most_recent(request):
    current_site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now(),
    )
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

    api.make_or_update_whatsup_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 1
    reminder = models.Reminder.on_site.first()
    assert reminder.deadline >= recent_task.created_on.date()


@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_is_always_scheduled_after_today(request):
    current_site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now(),
    )
    baker.make(
        tasks_models.Task,
        created_on=timezone.now() - datetime.timedelta(days=200),
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

    api.make_or_update_whatsup_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 1
    reminder = models.Reminder.on_site.first()
    assert reminder.deadline == timezone.localdate() + datetime.timedelta(6 * 7)


@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_with_task_on_site(request):
    current_site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now(),
    )
    baker.make(
        tasks_models.Task,
        project=project,
        public=True,
        site=current_site,
    )

    api.make_or_update_whatsup_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 1


@pytest.mark.django_db
def test_make_whatsup_reminder_with_task_off_site(request):
    current_site = get_current_site(request)
    other_site = baker.make(sites_models.Site)
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now(),
    )
    baker.make(
        tasks_models.Task,
        public=True,
        project=project,
        site=other_site,
    )

    api.make_or_update_whatsup_reminder(current_site, project)

    assert models.Reminder.on_site_to_send.count() == 0


@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_postpones_reminder_if_new_activity(request):
    current_site = get_current_site(request)
    yesterday = timezone.localdate() - datetime.timedelta(days=1)
    user = baker.make(auth_models.User)

    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now(),
    )
    assign_collaborator(user, project, is_owner=True)

    baker.make(
        tasks_models.Task,
        project=project,
        site=current_site,
        status=tasks_models.Task.PROPOSED,
        created_on=yesterday,
        public=True,
    )

    reminder = baker.make(
        models.Reminder,
        deadline=project.last_members_activity_at - datetime.timedelta(days=1),
        project=project,
        site=current_site,
        kind=models.Reminder.WHATS_UP,
    )

    project.last_members_activity_at = timezone.now()

    api.make_or_update_whatsup_reminder(current_site, project)

    reminder.refresh_from_db()
    assert reminder.deadline > project.last_members_activity_at.date()


@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_is_deleted_if_no_task(request, mocker):
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

    reminder = api.make_or_update_whatsup_reminder(current_site, project)

    assert reminder is None


@pytest.mark.django_db
def test_make_or_update_whatsup_reminder_with_sent_reminder_honors_interval(
    request,
):
    """Make sure we do not reschedule a reminder the day after the one sent"""
    current_site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        last_members_activity_at=timezone.now() - datetime.timedelta(days=10),
    )

    reminder = baker.make(
        models.Reminder,
        site=current_site,
        project=project,
        kind=models.Reminder.WHATS_UP,
        sent_on=timezone.localdate() - datetime.timedelta(days=2),
        deadline=timezone.localdate() - datetime.timedelta(days=6),
    )

    baker.make(
        tasks_models.Task,
        created_on=timezone.now() - datetime.timedelta(days=10),
        project=project,
        public=True,
        site=current_site,
        status=tasks_models.Task.INPROGRESS,
    )

    api.make_or_update_whatsup_reminder(current_site, project)

    reminder.refresh_from_db()

    assert models.Reminder.on_site_to_send.count() == 1
    assert models.Reminder.on_site_sent.count() == 1

    next_reminder = models.Reminder.on_site_to_send.first()

    assert (
        next_reminder.deadline
        == (reminder.sent_on + datetime.timedelta(days=6 * 7)).date()
    )


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
# Getting Recommendation
#################################################################


########################################################################
# Sending reminders
########################################################################

# FIXME pourquoi ces tests ne sont pas dans communication avec la commande
# senddigest ou la commande senddigest dans l'application courante ?


# eof
