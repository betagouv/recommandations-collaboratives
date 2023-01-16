# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""


import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from pytest_django.asserts import assertContains
from rest_framework.test import APIClient
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
    project = baker.make(models.Project, sites=[get_current_site(request)])
    url = reverse("projects-list")
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )
        response = client.get(url)

    assertContains(response, project.name)


@pytest.mark.django_db
def test_project_list_includes_project_in_switchtender_departments(request, client):
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        commune__department__code="01",
    )
    url = reverse("projects-list")
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(project.commune.department)
        response = client.get(url)

    assertContains(response, project.name)


@pytest.mark.django_db
def test_project_status_needs_authentication():
    client = APIClient()
    url = reverse("userprojectstatus-list")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_project_status_contains_only_my_projects(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    mine = baker.make(models.UserProjectStatus, user=user, site=site)
    other = baker.make(models.UserProjectStatus, site=site)  # noqa
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    first = response.data[0]
    assert first["id"] == mine.id
    assert first["project"]["id"] == mine.project.id


@pytest.mark.django_db
def test_user_project_status_contains_only_my_projects_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    local = baker.make(models.UserProjectStatus, user=user, site=site)
    other = baker.make(models.UserProjectStatus, user=user)  # noqa
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    first = response.data[0]
    assert first["id"] == local.id
    assert first["project"]["id"] == local.project.id


@pytest.mark.django_db
def test_access_my_user_project_status(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    mine = baker.make(models.UserProjectStatus, user=user, site=site)
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-detail", args=[mine.id])
    response = client.get(url)
    assert response.status_code == 200
    ups = response.data
    assert ups["id"] == mine.id
    assert ups["project"]["id"] == mine.project.id


@pytest.mark.django_db
def test_cannot_access_other_user_project_status(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    other = baker.make(models.UserProjectStatus, site=site)
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-detail", args=[other.id])
    response = client.get(url)
    assert response.status_code == 404


# eof
