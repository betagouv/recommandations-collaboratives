# encoding: utf-8

"""
test for project commands

authors: guillaume.libersat@beta.gouv.fr, sebastien.reuiller@beta.gouv.fr
created: 2024-01-22 15:26:00 CEST
"""

import logging
from datetime import datetime, timedelta

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.management import call_command
from django.utils import timezone
from model_bakery import baker

from recoco.apps.projects import models as projects_models
from recoco.utils import get_group_for_site


@pytest.mark.django_db
def test_command_update_inactive_flag_updates_fields(request, caplog):
    caplog.set_level(logging.DEBUG)

    site = get_current_site(request)

    advisor = baker.make(auth_models.User, username="advisor", email="jdoe@example.org")
    advisor.profile.sites.add(site)
    advisor.groups.add(get_group_for_site("advisor", site))

    user = baker.make(auth_models.User, username="jdoe", email="jdoe@example.org")
    user.profile.sites.add(site)

    project = baker.make(
        projects_models.Project,
        name="A project",
        sites=[site],
        members=[user],
        created_on=datetime(2010, 1, 1, 12, 0, 0),
    )

    assert project.inactive_since is None

    call_command("update_inactive_flag")

    output = "\n".join([str(record.message) for record in caplog.records])

    project.refresh_from_db()

    assert "Setting 1 projects as inactive" in output

    assert project.inactive_since is not None
    assert project.inactive_reason


@pytest.mark.django_db
def test_command_update_inactive_flag_honors_dry_run(request, caplog):
    caplog.set_level(logging.DEBUG)

    site = get_current_site(request)

    advisor = baker.make(auth_models.User, username="advisor", email="jdoe@example.org")
    advisor.profile.sites.add(site)
    advisor.groups.add(get_group_for_site("advisor", site))

    user = baker.make(auth_models.User, username="jdoe", email="jdoe@example.org")
    user.profile.sites.add(site)

    project = baker.make(
        projects_models.Project,
        name="A project",
        sites=[site],
        members=[user],
        created_on=datetime(2010, 1, 1, 12, 0, 0),
    )

    assert project.inactive_since is None

    call_command("update_inactive_flag", dry_run=True)

    output = "\n".join([str(record.message) for record in caplog.records])

    project.refresh_from_db()

    assert "Would set 1 projects as inactive" in output

    assert project.inactive_since is None
    assert not project.inactive_reason


@pytest.mark.django_db
def test_command_update_inactive_flag_honors_project_creation_date(request):
    site = get_current_site(request)

    advisor = baker.make(auth_models.User, username="advisor", email="jdoe@example.org")
    advisor.profile.sites.add(site)
    advisor.groups.add(get_group_for_site("advisor", site))

    user = baker.make(auth_models.User, username="jdoe", email="jdoe@example.org")
    user.profile.sites.add(site)

    project = baker.make(
        projects_models.Project, name="A project", sites=[site], members=[user]
    )

    call_command("update_inactive_flag")

    project.refresh_from_db()

    assert project.inactive_since is None


@pytest.mark.django_db
def test_command_update_inactive_flag_handles_never_logged_in_users(request):
    site = get_current_site(request)

    user = baker.make(
        auth_models.User, username="jdoe", email="jdoe@example.org", last_login=None
    )
    user.profile.sites.add(site)

    project = baker.make(
        projects_models.Project,
        name="A project",
        sites=[site],
        members=[user],
        created_on=datetime(2010, 1, 1, 12, 0, 0),
    )

    call_command("update_inactive_flag")

    project.refresh_from_db()

    assert project.inactive_since == project.created_on + timedelta(30 * 12)  # XXX
    # Hardcoded


@pytest.mark.django_db
def test_command_update_inactive_flag_honors_existing_inactivity_date(request):
    site = get_current_site(request)

    user = baker.make(
        auth_models.User, username="jdoe", email="jdoe@example.org", last_login=None
    )
    user.profile.sites.add(site)

    inactive_since = timezone.now() - timedelta(days=60)

    project = baker.make(
        projects_models.Project,
        name="A project",
        sites=[site],
        members=[user],
        created_on=datetime(2010, 1, 1, 12, 0, 0),
        inactive_since=inactive_since,
    )

    call_command("update_inactive_flag")

    project.refresh_from_db()

    assert project.inactive_since == inactive_since


@pytest.mark.django_db
def test_command_update_inactive_flag_honors_manual_reactivation(request):
    site = get_current_site(request)

    user = baker.make(
        auth_models.User, username="jdoe", email="jdoe@example.org", last_login=None
    )
    user.profile.sites.add(site)

    last_manual_reactivation = timezone.now() - timedelta(days=30)

    project = baker.make(
        projects_models.Project,
        name="A project",
        sites=[site],
        members=[user],
        created_on=datetime(2010, 1, 1, 12, 0, 0),
        last_manual_reactivation=last_manual_reactivation,
    )

    assert project.inactive_since is None

    call_command("update_inactive_flag")

    project.refresh_from_db()

    assert project.inactive_since is None
