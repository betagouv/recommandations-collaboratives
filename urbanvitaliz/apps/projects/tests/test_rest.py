# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""


import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains
from urbanvitaliz.utils import login

from .. import models


########################################################################
# REST API
########################################################################
@pytest.mark.django_db
def test_anonymous_cannot_use_project_api(client):
    url = reverse("projects-list")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_in_user_can_use_project_api(client):
    url = reverse("projects-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_list_includes_project_for_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-list")
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        response = client.get(url)

    assertContains(response, project.name)


@pytest.mark.django_db
def test_project_list_includes_project_in_switchtender_departments(request, client):
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        commune__department__code="01",
    ).make()
    url = reverse("projects-list")
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(project.commune.department)
        response = client.get(url)

    assertContains(response, project.name)
