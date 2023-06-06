# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""


import pytest
from actstream.models import user_stream
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from notifications.signals import notify
from pytest_django.asserts import assertContains, assertNotContains
from rest_framework.test import APIClient

from urbanvitaliz.utils import get_group_for_site, login

from .. import models, utils


########################################################################
# REST API: projects
########################################################################

# FIXME pourquoi est ce que ces tests n'utilisent pas le APIClient ?


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
def test_project_list_includes_only_projects_in_switchtender_departments(
    request, client
):
    user = baker.make(auth_models.User, email="me@example.com")
    site = get_current_site(request)
    # my project and details
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        commune__name="Ma Comune",
        commune__department__code="01",
        commune__department__name="Mon Departement",
        name="Mon project",
    )
    unwanted_project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        commune__department__code="02",
    )

    utils.assign_advisor(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("projects-list")
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1

    data = response.data[0]

    # project fields: not ideal
    expected = [
        "commune",
        "created_on",
        "id",
        "is_observer",
        "is_switchtender",
        "name",
        "notifications",
        "org_name",
        "private_message_count",
        "public_message_count",
        "recommendation_count",
        "status",
        "switchtenders",
        "updated_on",
    ]
    assert set(data.keys()) == set(expected)

    assert data["name"] == project.name


########################################################################
# user project statuses
########################################################################


@pytest.mark.django_db
def test_project_status_needs_authentication():
    client = APIClient()
    url = reverse("userprojectstatus-list")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_project_status_contains_only_my_projects(request):
    user = baker.make(auth_models.User, email="me@example.com")
    site = get_current_site(request)
    # my project and details
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        commune__name="Ma Comune",
        commune__department__name="Mon Departement",
        name="Mon project",
    )
    mine = baker.make(models.UserProjectStatus, user=user, site=site, project=project)

    baker.make(
        models.ProjectSwitchtender, site=site, switchtender=user, project=project
    )
    # a public note with notification
    pub_note = baker.make(models.Note, public=True, project=mine.project)
    verb = "a envoyé un message"
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=pub_note,
        target=project,
        private=True,  # XXX why is private true?
    )

    # a private note with notification
    priv_note = baker.make(models.Note, public=False, project=mine.project)
    verb = "a envoyé un message dans l'espace conseillers"
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=priv_note,
        target=project,
        private=True,
    )

    # another one not for me
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

    assert len(first["project"]["switchtenders"]) == 1
    switchtender = first["project"]["switchtenders"][0]
    assert switchtender["email"] == user.email

    # user project status fields
    assert set(first.keys()) == set(["id", "project", "status"])

    # project fields: not ideal
    expected = [
        "commune",
        "created_on",
        "id",
        "is_observer",
        "is_switchtender",
        "name",
        "notifications",
        "org_name",
        "private_message_count",
        "public_message_count",
        "recommendation_count",
        "status",
        "switchtenders",
        "updated_on",
    ]
    assert set(first["project"].keys()) == set(expected)
    assert first["project"]["is_switchtender"] == True
    assert first["project"]["is_observer"] == False


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
def test_regional_actor_can_see_project_tasks_for_site(request):
    user = baker.make(auth_models.User)

    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    baker.make(models.Task, project=project, public=True)
    utils.assign_observer(user, project, site)

    client = APIClient()
    with login(client, groups=["example_com_advisor"]) as user:
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
def test_user_cannot_see_project_tasks_when_not_in_relation(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_collaborator_can_move_project_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, status="READY", sites=[site])
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-move", args=[project.id, tasks[0].id])
    response = client.post(url, data={"above": tasks[1].id})

    assert response.status_code == 200
    assert response.data == {"status": "insert above done"}


@pytest.mark.django_db
def test_project_observer_can_move_project_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    utils.assign_observer(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-move", args=[project.id, tasks[0].id])
    response = client.post(url, data={"above": tasks[1].id})

    assert response.status_code == 200


@pytest.mark.django_db
def test_project_advisor_can_move_project_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    utils.assign_advisor(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-move", args=[project.id, tasks[0].id])
    response = client.post(url, data={"above": tasks[1].id})

    assert response.status_code == 200


@pytest.mark.django_db
def test_updating_user_project_is_logged(request):
    user = baker.make(auth_models.User, username="Bob")
    site = get_current_site(request)
    ups = baker.make(models.UserProjectStatus, user=user, site=site, status="DRAFT")

    to_update = {"status": "DONE"}

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-detail", args=[ups.id])
    response = client.patch(url, data=to_update)

    assert response.status_code == 200
    updated_ups = response.data
    assert updated_ups["status"] == to_update["status"]

    stream = user_stream(user, with_user_activity=True)
    assert stream.count() == 1
    assert stream[0].verb == "a changé l'état de son suivi"


# eof
