# encoding: utf-8

"""
test for senddigests command

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-11 15:26:00 CEST
"""

import datetime
import io

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from model_bakery import baker
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.reminders import models as reminders_models
from urbanvitaliz.apps.projects.utils import assign_advisor, assign_collaborator
from urbanvitaliz.apps.tasks import models as task_models
from urbanvitaliz.utils import get_group_for_site


@pytest.mark.django_db
@override_settings(BREVO_FORCE_DEBUG=True)
def test_command_send_digest_to_active_users(request, mocker):
    site = get_current_site(request)

    advisor = baker.make(auth_models.User, username="advisor", email="jdoe@example.org")
    advisor.profile.sites.add(site)
    advisor.groups.add(get_group_for_site("advisor", site))

    user = baker.make(auth_models.User, username="jdoe", email="jdoe@example.org")
    user.profile.sites.add(site)

    project = baker.make(
        projects_models.Project, name="A project", sites=[site], members=[user]
    )
    # FIXME pourquoi ne met pas aussi dans advisor group for site ?
    assign_advisor(advisor, project, site)

    baker.make(task_models.Task, created_by=advisor, project=project, site=site)

    out = io.StringIO()

    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digests_reminders_by_project",
        return_value=False,
    )
    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digests_for_new_recommendations_by_user"
    )
    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digest_for_non_switchtender_by_user"
    )
    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digests_for_new_sites_by_user"
    )
    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digest_for_switchtender_by_user"
    )

    call_command("senddigests", stdout=out)

    output = out.getvalue()

    expected = f"""
#### Sending digests for site <example.com> ####

** Sending Task Reminders **
Sent reminder digest for AnonymousUser
Sent reminder digest for {advisor.username}
Sent reminder digest for {user.username}
** Sending new recommendations digests **
Sent new reco digest for {user.username} on {project.name}
** Sending general digests **
Sent general digest for AnonymousUser
Sent general digest for {user.username}
** Sending general switchtender digests **
* Sent new site digest for {advisor.username}
* Sent general digest for switchtender (to {advisor.username})
"""
    assert output == expected


@pytest.mark.django_db
@override_settings(BREVO_FORCE_DEBUG=True)
def test_command_do_not_send_digest_to_deactivated_users(request, mocker):
    site = get_current_site(request)

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

    out = io.StringIO()

    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digests_reminders_by_project",
        return_value=False,
    )
    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digests_for_new_recommendations_by_user",
    )
    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digest_for_non_switchtender_by_user"
    )
    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digests_for_new_sites_by_user"
    )
    mocker.patch(
        "urbanvitaliz.apps.communication.digests.send_digest_for_switchtender_by_user"
    )

    call_command("senddigests", stdout=out)

    output = out.getvalue()

    expected = """
#### Sending digests for site <example.com> ####

** Sending Project Reminders **
Failed sending reminder digest for project A project (1) -- NO OWNER
** Sending new recommendations digests **
** Sending general digests **
Sent general digest
** Sending general switchtender digests **
"""
    assert output == expected


#################################################################
# Reminders
#################################################################
@pytest.mark.django_db
@override_settings(BREVO_FORCE_DEBUG=True)
def test_command_pending_recommendation_reminder_sent(request, mocker):
    current_site = get_current_site(request)
    yesterday = timezone.localdate() - datetime.timedelta(days=1)
    user = baker.make(auth_models.User)

    project = baker.make(projects_models.Project, sites=[current_site])
    assign_collaborator(user, project, is_owner=True)

    print("owner=", project.owner)

    baker.make(
        task_models.Task,
        project=project,
        site=current_site,
        status=task_models.Task.PROPOSED,
        created_on=yesterday - datetime.timedelta(days=10),
        public=True,
    )

    baker.make(
        reminders_models.Reminder,
        deadline=yesterday,
        project=project,
        site=current_site,
        kind=reminders_models.Reminder.NEW_RECO,
    )

    call_command("senddigests")

    assert reminders_models.Reminder.to_send.count() == 0
    assert reminders_models.Reminder.sent.count() == 1


@pytest.mark.django_db
@override_settings(BREVO_FORCE_DEBUG=True)
def test_command_pending_recommendation_reminder_not_send_if_no_owner(request, mocker):
    current_site = get_current_site(request)
    yesterday = timezone.localdate() - datetime.timedelta(days=1)
    user = baker.make(auth_models.User)
    project = baker.make(projects_models.Project, sites=[current_site])
    assign_collaborator(user, project, is_owner=False)
    baker.make(
        reminders_models.Reminder,
        deadline=yesterday,
        project=project,
        site=current_site,
        kind=reminders_models.Reminder.NEW_RECO,
    )

    call_command("senddigests")

    assert reminders_models.Reminder.to_send.count() == 1
    assert reminders_models.Reminder.sent.count() == 0


@pytest.mark.django_db
@override_settings(BREVO_FORCE_DEBUG=True)
def test_command_do_not_send_pending_reminder_with_future_deadline(request, mocker):
    current_site = get_current_site(request)

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    user = baker.make(auth_models.User)
    project = baker.make(projects_models.Project, sites=[current_site])

    assign_collaborator(user, project, is_owner=True)

    baker.make(
        reminders_models.Reminder,
        deadline=tomorrow,
        kind=reminders_models.Reminder.NEW_RECO,
    )

    mocker.patch("urbanvitaliz.apps.communication.api.send_debug_email")

    call_command("senddigests")

    assert reminders_models.Reminder.to_send.count() == 1
    assert reminders_models.Reminder.sent.count() == 0

    # communication_api.send_debug_email.assert_not_called()


# eof
