# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""


import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker
from urbanvitaliz import utils

from .. import models
from ..templatetags import projects_extra

########################################################################
# template tags and filters
########################################################################


@pytest.mark.django_db
def test_current_project_tag(request):
    current_site = get_current_site(request)
    project = baker.make(models.Project, sites=[current_site])
    session = {"project_id": project.id}
    assert projects_extra.current_project(session) == project


@pytest.mark.django_db
def test_is_staff_for_current_site_success(request):
    site = get_current_site(request)
    group = utils.get_group_for_site("staff", site)
    user = baker.make(auth.User)
    user.groups.add(group)
    assert projects_extra.is_staff_for_current_site(user) is True


@pytest.mark.django_db
def test_is_staff_for_current_site_failure(request):
    user = baker.make(auth.User)
    assert projects_extra.is_staff_for_current_site(user) is False


#
# advising position

@pytest.mark.django_db
def test_advising_position_for_user_when_nothing(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    user = baker.make(auth.User)
    expected = {"is_observer": False, "is_advisor": False}
    assert projects_extra.get_advising_position(user, project) == expected


@pytest.mark.django_db
def test_advising_position_for_user_when_advisor(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    user = baker.make(auth.User)
    baker.make(
        models.ProjectSwitchtender,
        switchtender=user,
        project=project,
        site=site,
        is_observer=False,
    )
    expected = {"is_observer": False, "is_advisor": True}
    assert projects_extra.get_advising_position(user, project) == expected


@pytest.mark.django_db
def test_advising_position_for_user_when_observer(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    user = baker.make(auth.User)
    baker.make(
        models.ProjectSwitchtender,
        switchtender=user,
        project=project,
        site=site,
        is_observer=True,
    )
    expected = {"is_observer": True, "is_advisor": False}
    assert projects_extra.get_advising_position(user, project) == expected


# eof
