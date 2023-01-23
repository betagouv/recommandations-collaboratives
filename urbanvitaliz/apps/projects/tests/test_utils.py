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
from model_bakery.recipe import Recipe
from urbanvitaliz.apps.geomatics import models as geomatics

from .. import models, utils


@pytest.mark.django_db
def test_contributor_has_the_same_rights_as_the_owner(client):
    membership_owner = baker.make(models.ProjectMember, is_owner=True)
    membership_contrib = baker.make(models.ProjectMember)

    project = Recipe(
        models.Project,
        projectmember_set=[membership_owner, membership_contrib],
        status="READY",
    ).make()

    assert utils.can_manage_project(project, membership_owner.member)
    assert utils.can_manage_project(project, membership_contrib.member)


@pytest.mark.django_db
def test_switchtender_can_manage_project(request, client):
    switchtender = Recipe(auth.User).make()
    group = auth.Group.objects.get(name="switchtender")
    switchtender.groups.add(group)
    project = Recipe(models.Project, status="READY").make()
    project.switchtenders_on_site.create(
        switchtender=switchtender, site=get_current_site(request)
    )

    assert utils.can_manage_project(project, switchtender)


@pytest.mark.django_db
def test_non_switchtender_cannot_administrate_project(client):
    someone = Recipe(auth.User).make()
    project = Recipe(models.Project, status="READY").make()

    assert not utils.can_manage_project(project, someone)


@pytest.mark.django_db
def test_get_regional_actors_for_project(client, request):
    group = auth.Group.objects.get(name="switchtender")

    dept62 = baker.make(geomatics.Department, code="62")
    dept80 = baker.make(geomatics.Department, code="80")
    dept59 = baker.make(geomatics.Department, code="59")

    site = get_current_site(request)

    switchtenderA = baker.make(auth.User, groups=[group])
    switchtenderA.profile.departments.set([dept62, dept80])
    switchtenderA.profile.sites.set([site])

    switchtenderB = baker.make(auth.User, groups=[group])
    switchtenderB.profile.departments.set([dept59, dept80])
    switchtenderB.profile.sites.set([site])

    switchtenderC = baker.make(auth.User, groups=[group])
    switchtenderC.profile.departments.set([])
    switchtenderC.profile.sites.set([site])

    switchtenderD = baker.make(auth.User, groups=[group])
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

    group = auth.Group.objects.get(name="switchtender")

    dept62 = baker.make(geomatics.Department, code="62")

    switchtender = baker.make(auth.User, groups=[group])
    switchtender.profile.departments.set([dept62])

    userA = baker.make(auth.User)
    userB = baker.make(auth.User)

    project = baker.make(models.Project, sites=[current_site], status="READY")
    project.switchtenders_on_site.create(switchtender=userA, site=current_site)

    assert utils.can_administrate_project(project=None, user=userA)
    assert not utils.can_administrate_project(project=None, user=userB)
