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

from .. import models, utils


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

    assert utils.can_administrate_project(project, owner)
    assert utils.can_administrate_project(project, contributor)


@pytest.mark.django_db
def test_switchtender_can_administrate_project(client):
    switchtender = Recipe(auth.User).make()
    group = auth.Group.objects.get(name="switchtender")
    switchtender.groups.add(group)
    project = Recipe(models.Project, status="READY").make()

    assert utils.can_administrate_project(project, switchtender)


@pytest.mark.django_db
def test_non_switchtender_cannot_administrate_project(client):
    someone = Recipe(auth.User).make()
    project = Recipe(models.Project, status="READY").make()

    assert not utils.can_administrate_project(project, someone)


@pytest.mark.django_db
def test_get_switchtender_for_project(client):
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

    selected_switchtenders = utils.get_switchtenders_for_project(project)

    assert len(selected_switchtenders) == 2
    assert switchtenderA in selected_switchtenders
    assert switchtenderB not in selected_switchtenders
    assert switchtenderC in selected_switchtenders
