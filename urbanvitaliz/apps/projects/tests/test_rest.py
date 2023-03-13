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
from .. import utils

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
def test_project_list_includes_project_for_advisor(request, client):
    current_site = get_current_site(request)
    project = baker.make(models.Project, commune__name="Lille", sites=[current_site])
    url = reverse("projects-list")

    with login(client, groups=["example_com_advisor"]):
        response = client.get(url)

    assertContains(response, project.name)


@pytest.mark.django_db
def test_project_list_includes_project_for_staff(request, client):
    current_site = get_current_site(request)
    project = baker.make(models.Project, sites=[current_site])
    url = reverse("projects-list")

    with login(client, groups=["example_com_staff"]):
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
    with login(client, groups=["example_com_advisor"]) as user:
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
def test_advisor_access_new_regional_project_status(request):
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        commune__department__code="01",
    )

    group = auth_models.Group.objects.get(name="example_com_advisor")
    user = baker.make(auth_models.User, groups=[group])
    user.profile.departments.add(project.commune.department)

    site = get_current_site(request)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = client.get(url)
    assert response.status_code == 200
    ups = response.data
    assert len(ups) == 1
    assert ups[0]["project"]["id"] == project.id


@pytest.mark.django_db
def test_advisor_access_makes_no_user_project_status_duplicate(request):
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        commune__department__code="01",
    )

    group = auth_models.Group.objects.get(name="example_com_advisor")
    user = baker.make(auth_models.User, groups=[group])
    user.profile.departments.add(project.commune.department)

    baker.make(
        models.UserProjectStatus,
        project=project,
        site=get_current_site(request),
        user=user,
    )

    site = get_current_site(request)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = client.get(url)
    assert response.status_code == 200
    ups = response.data
    assert len(ups) == 1
    assert ups[0]["project"]["id"] == project.id


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


########################################################################
# tasks
########################################################################


@pytest.mark.django_db
def test_project_collaborator_can_see_project_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    baker.make(models.Task, project=project, public=True)
    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200
    assert set(e["id"] for e in response.data) == set(t.id for t in tasks)


@pytest.mark.django_db
def test_project_observer_can_see_project_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    baker.make(models.Task, project=project, public=True)
    utils.assign_observer(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200
    assert set(e["id"] for e in response.data) == set(t.id for t in tasks)


@pytest.mark.django_db
def test_project_advisor_can_see_project_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    baker.make(models.Task, project=project, public=True)
    utils.assign_advisor(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200
    assert set(e["id"] for e in response.data) == set(t.id for t in tasks)


@pytest.mark.django_db
def test_user_cannot_see_project_tasks_when_not_collaborator(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    tasks = baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 403


# eof
