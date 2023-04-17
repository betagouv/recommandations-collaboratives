# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-01-18 10:11:56 CEST
"""


import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects.utils import assign_advisor

from .. import models, utils


@pytest.mark.django_db
def test_get_regional_actors_for_project(client, request):
    group_current_site = auth.Group.objects.get(name="example_com_advisor")
    group_other_site, _ = auth.Group.objects.get_or_create(name="another_com_advisor")

    dept62 = baker.make(geomatics.Department, code="62")
    dept80 = baker.make(geomatics.Department, code="80")
    dept59 = baker.make(geomatics.Department, code="59")

    site = get_current_site(request)

    switchtenderA = baker.make(auth.User, groups=[group_current_site])
    switchtenderA.profile.departments.set([dept62, dept80])

    switchtenderB = baker.make(auth.User, groups=[group_current_site])
    switchtenderB.profile.departments.set([dept59, dept80])

    switchtenderC = baker.make(auth.User, groups=[group_current_site])
    switchtenderC.profile.departments.set([])

    switchtenderD = baker.make(auth.User, groups=[group_other_site])
    switchtenderD.profile.departments.set([dept59, dept62])

    project = baker.make(models.Project, status="READY", commune__department=dept62)

    selected_actors = utils.get_regional_actors_for_project(site, project)

    assert len(selected_actors) == 1
    assert switchtenderA in selected_actors
    assert switchtenderB not in selected_actors
    assert switchtenderC not in selected_actors
    assert switchtenderD not in selected_actors


@pytest.mark.django_db
def test_check_if_switchtends_any_project(request, client):
    current_site = get_current_site(request)

    group = auth.Group.objects.get(name="example_com_advisor")

    dept62 = baker.make(geomatics.Department, code="62")

    switchtender = baker.make(auth.User, groups=[group])
    switchtender.profile.departments.set([dept62])

    userA = baker.make(auth.User)
    userB = baker.make(auth.User)

    project = baker.make(models.Project, sites=[current_site], status="READY")
    assign_advisor(userA, project, current_site)

    assert utils.can_administrate_project(project=None, user=userA)
    assert not utils.can_administrate_project(project=None, user=userB)
