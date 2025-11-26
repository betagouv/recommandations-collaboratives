# encoding: utf-8

"""
test for senddigests command

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-11 15:26:00 CEST
"""

import datetime
import logging

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.management import call_command
from django.utils import timezone
from model_bakery import baker

from recoco.apps.home import models as home_models
from recoco.apps.projects import models as projects_models
from recoco.apps.projects.utils import assign_advisor, assign_collaborator
from recoco.apps.reminders import models as reminders_models
from recoco.apps.tasks import models as task_models
from recoco.utils import get_group_for_site

from .. import digests


@pytest.mark.django_db
def test_command_send_digest_executes_all_tasks(request, mocker, caplog, make_project):
    caplog.set_level(logging.DEBUG)

    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    advisor = baker.make(auth_models.User, username="advisor", email="jdoe@example.org")
    advisor.profile.sites.add(site)
    advisor.groups.add(get_group_for_site("advisor", site))

    user = baker.make(auth_models.User, username="jdoe", email="jdoe@example.org")
    user.profile.sites.add(site)

    project = make_project(name="A project", site=site, members=[user])
    # FIXME(raph) pourquoi ne met pas aussi dans advisor group for site ?
    # 23/11/03: (glibersat) pas compris @raph
    assign_advisor(advisor, project, site)

    baker.make(task_models.Task, created_by=advisor, project=project, site=site)

    mocker.patch(
        "recoco.apps.communication.digests.send_reminder_digests_by_project",
        return_value=False,
    )
    mocker.patch(
        "recoco.apps.communication.digests.send_digests_for_new_recommendations_by_user"
    )
    mocker.patch(
        "recoco.apps.communication.digests.send_digest_for_non_switchtender_by_user"
    )
    mocker.patch("recoco.apps.communication.digests.send_digests_for_new_sites_by_user")
    mocker.patch(
        "recoco.apps.communication.digests.send_digest_for_switchtender_by_user"
    )

    call_command("senddigests")

    output = "\n".join([str(record.message) for record in caplog.records])

    expected_headings = [
        "Sending digests for site <example.com>",
        "Sending Project Reminders",
        "Sending new recommendations digests",
        "Sending general digests",
        "Sending general switchtender digests",
        f"Sent new site digest for {advisor}",
    ]

    for heading in expected_headings:
        assert heading in output


@pytest.mark.django_db
def test_command_do_not_send_digest_to_deactivated_users(request, mocker, caplog):
    caplog.set_level(logging.DEBUG)

    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    advisor = baker.make(
        auth_models.User, username="advisor", email="jdoe@example.org", is_active=False
    )
    advisor.profile.sites.add(site)
    advisor.groups.add(get_group_for_site("advisor", site))

    user = baker.make(
        auth_models.User, username="jdoe", email="jdoe@example.org", is_active=False
    )
    profile = user.profile
    profile.sites.add(site)
    profile.deleted = timezone.now()
    profile.save()

    project = baker.make(
        projects_models.Project, id=1, name="A project", sites=[site], members=[user]
    )
    # FIXME pourquoi ne met pas aussi dans advisor group for site ?
    assign_advisor(advisor, project, site)

    baker.make(task_models.Task, created_by=advisor, project=project, site=site)

    mocker.patch(
        "recoco.apps.communication.digests.send_reminder_digests_by_project",
        return_value=False,
    )
    mocker.patch(
        "recoco.apps.communication.digests.send_digests_for_new_recommendations_by_user",
    )
    mocker.patch(
        "recoco.apps.communication.digests.send_digest_for_non_switchtender_by_user"
    )
    mocker.patch("recoco.apps.communication.digests.send_digests_for_new_sites_by_user")
    mocker.patch(
        "recoco.apps.communication.digests.send_digest_for_switchtender_by_user"
    )

    call_command("senddigests")

    output = "\n".join([str(record.message) for record in caplog.records])

    unexpected_logs = [f"{user}", f"{advisor}"]

    for log in unexpected_logs:
        assert log not in output


#################################################################
# Reminders
#################################################################
@pytest.mark.django_db
def test_command_reminder_are_treated(request, mocker, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    user = baker.make(auth_models.User)

    assign_collaborator(user, project, is_owner=True)

    mocker.patch("recoco.apps.communication.digests.send_reminder_digests_by_project")

    call_command("senddigests")

    digests.send_reminder_digests_by_project.assert_called()


@pytest.mark.django_db
def test_command_pending_recommendation_reminder_sent(request, mocker, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    user = baker.make(auth_models.User)

    assign_collaborator(user, project, is_owner=True)

    mocker.patch(
        "recoco.apps.communication.digests.send_new_recommendations_reminders_digest_by_project"
    )

    mocker.patch(
        "recoco.apps.communication.digests.send_whatsup_reminders_digest_by_project"
    )

    call_command("senddigests")

    digests.send_new_recommendations_reminders_digest_by_project.assert_called()
    digests.send_whatsup_reminders_digest_by_project.assert_called()


@pytest.mark.django_db
def test_command_pending_recommendation_reminder_not_sent_if_advisor(
    request, mocker, project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    advisor = baker.make(auth_models.User)
    collaborator = baker.make(auth_models.User)

    assign_advisor(advisor, project, current_site)
    assign_collaborator(collaborator, project, is_owner=True)

    mocker.patch(
        "recoco.apps.communication.digests.send_new_recommendations_reminders_digest_by_project"
    )

    mocker.patch(
        "recoco.apps.communication.digests.send_whatsup_reminders_digest_by_project"
    )

    call_command("senddigests")

    digests.send_new_recommendations_reminders_digest_by_project.assert_called_once()
    digests.send_whatsup_reminders_digest_by_project.assert_called_once()


@pytest.mark.django_db
def test_command_pending_reminder_sent_and_rescheduled(request, mocker, make_project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    user = baker.make(auth_models.User)

    project = make_project(
        site=current_site,
        last_members_activity_at=timezone.now() - datetime.timedelta(days=6 * 7),
    )

    baker.make(
        task_models.Task,
        created_on=timezone.now() - datetime.timedelta(days=6 * 7),
        project=project,
        public=True,
        site=current_site,
        status=task_models.Task.INPROGRESS,
    )

    assign_collaborator(user, project, is_owner=True)

    call_command("senddigests")

    assert reminders_models.Reminder.on_site_to_send.count() == 1
    assert reminders_models.Reminder.on_site_sent.count() == 2


@pytest.mark.django_db
def test_command_pending_recommendation_reminder_not_send_if_no_owner(
    request, mocker, project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    mocker.patch(
        "recoco.apps.communication.digests.send_new_recommendations_reminders_digest_by_project"
    )
    mocker.patch(
        "recoco.apps.communication.digests.send_whatsup_reminders_digest_by_project"
    )

    call_command("senddigests")

    digests.send_new_recommendations_reminders_digest_by_project.assert_not_called()
    digests.send_whatsup_reminders_digest_by_project.assert_not_called()


@pytest.mark.django_db
def test_command_pending_reminders_not_sent_if_project_inactive(
    request, mocker, make_project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    user = baker.make(auth_models.User)

    project = make_project(site=current_site, inactive_since=timezone.now())
    assign_collaborator(user, project, is_owner=True)

    mocker.patch(
        "recoco.apps.communication.digests.send_new_recommendations_reminders_digest_by_project"
    )
    mocker.patch(
        "recoco.apps.communication.digests.send_whatsup_reminders_digest_by_project"
    )

    call_command("senddigests")

    digests.send_new_recommendations_reminders_digest_by_project.assert_not_called()
    digests.send_whatsup_reminders_digest_by_project.assert_not_called()


@pytest.mark.django_db
def test_command_pending_reminders_not_sent_if_project_muted(
    request, mocker, make_project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    user = baker.make(auth_models.User)

    project = make_project(site=current_site, muted=True)
    assign_collaborator(user, project, is_owner=True)

    mocker.patch(
        "recoco.apps.communication.digests.send_new_recommendations_reminders_digest_by_project"
    )
    mocker.patch(
        "recoco.apps.communication.digests.send_whatsup_reminders_digest_by_project"
    )

    call_command("senddigests")

    digests.send_new_recommendations_reminders_digest_by_project.assert_not_called()
    digests.send_whatsup_reminders_digest_by_project.assert_not_called()


# eof
