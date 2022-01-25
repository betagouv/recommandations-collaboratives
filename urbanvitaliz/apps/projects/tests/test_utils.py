# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-01-18 10:11:56 CEST
"""


import pytest
from django.contrib.auth import models as auth
from model_bakery import baker
from model_bakery.recipe import Recipe
from urbanvitaliz.apps.geomatics import models as geomatics

from .. import models, signals, utils


@pytest.mark.django_db
def test_contributor_has_the_same_rights_as_the_owner(client):
    owner = Recipe(auth.User, username="owner", email="owner@example.com").make()
    contributor = Recipe(
        auth.User, username="contributor", email="contributor@example.com"
    ).make()
    project = Recipe(
        models.Project,
        email=owner.email,
        emails=[owner.email, contributor.email],
        status="READY",
    ).make()

    assert utils.can_manage_project(project, owner)
    assert utils.can_manage_project(project, contributor)


@pytest.mark.django_db
def test_switchtender_can_manage_project(client):
    switchtender = Recipe(auth.User).make()
    group = auth.Group.objects.get(name="switchtender")
    switchtender.groups.add(group)
    project = Recipe(models.Project, status="READY").make()
    project.switchtenders.add(switchtender)

    assert utils.can_manage_project(project, switchtender)


@pytest.mark.django_db
def test_non_switchtender_cannot_administrate_project(client):
    someone = Recipe(auth.User).make()
    project = Recipe(models.Project, status="READY").make()

    assert not utils.can_manage_project(project, someone)


@pytest.mark.django_db
def test_get_regional_actors_for_project(client):
    group = auth.Group.objects.get(name="switchtender")

    dept62 = baker.make(geomatics.Department, code="62")
    dept80 = baker.make(geomatics.Department, code="80")
    dept59 = baker.make(geomatics.Department, code="59")

    switchtenderA = baker.make(auth.User, groups=[group])
    switchtenderA.profile.departments.set([dept62, dept80])

    switchtenderB = baker.make(auth.User, groups=[group])
    switchtenderB.profile.departments.set([dept59, dept80])

    switchtenderC = baker.make(auth.User, groups=[group])
    switchtenderC.profile.departments.set([])

    project = baker.make(models.Project, status="READY", commune__department=dept62)

    selected_actors = utils.get_regional_actors_for_project(project)

    assert len(selected_actors) == 1
    assert switchtenderA in selected_actors
    assert switchtenderB not in selected_actors
    assert switchtenderC not in selected_actors
