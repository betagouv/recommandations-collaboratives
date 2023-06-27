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
from pytest_django.asserts import assertContains
from rest_framework.test import APIClient

from urbanvitaliz.utils import login
from urbanvitaliz import verbs

from .. import models, utils


########################################################################
# list of projects
########################################################################

# FIXME pourquoi est ce que ces tests n'utilisent pas le APIClient ?


@pytest.mark.django_db
def test_anonymous_cannot_use_project_list_api(client):
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

    # a public note with notification
    pub_note = baker.make(models.Note, public=True, project=project)
    verb = "a envoyé un message"
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=pub_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    # a private note with notification for someone else
    priv_note = baker.make(models.Note, public=False, project=project)
    verb = "a envoyé un message dans l'espace conseillers"
    notify.send(
        sender=user,
        recipient=baker.make(auth_models.User),
        verb=verb,
        action_object=priv_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    baker.make(  # unwanted project
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
        "status",
        "switchtenders",
        "updated_on",
    ]
    assert set(data.keys()) == set(expected)

    assert data["name"] == project.name
    assert data["is_switchtender"] is True
    assert data["is_observer"] is False
    assert data["notifications"] == {
        "count": 1,
        "has_collaborator_activity": True,
        "new_recommendations": 0,
        "unread_private_messages": 0,
        "unread_public_messages": 1,
        "project_id": str(project.id),
    }


########################################################################
# get project details
########################################################################


@pytest.mark.django_db
def test_anonymous_cannot_use_project_detail_api(request, client):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])

    client = APIClient()

    url = reverse("projects-detail", args=[project.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_detail_contains_project_info(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    project = create_project_with_notifications(site, user)

    utils.assign_advisor(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("projects-detail", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200

    data = response.data
    check_project_content(project, data)


def create_project_with_notifications(site, user):
    """Create a new project with user as advisor and notifications

    To keep in sync with check_project_content
    """
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

    # a public note with notification
    pub_note = baker.make(models.Note, public=True, project=project)
    verb = "a envoyé un message"
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=pub_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    # a private note with notification for someone else
    priv_note = baker.make(models.Note, public=False, project=project)
    verb = "a envoyé un message dans l'espace conseillers"
    notify.send(
        sender=user,
        recipient=baker.make(auth_models.User),
        verb=verb,
        action_object=priv_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    return project


def check_project_content(project, data):
    """Check project content provided as json

    To keep in sync with create_project_with_notifications
    """
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
        "status",
        "switchtenders",
        "updated_on",
        "private_message_count",
        "public_message_count",
        "recommendation_count",
    ]
    assert set(data.keys()) == set(expected)

    assert data["name"] == project.name
    assert data["is_switchtender"] is True
    assert data["is_observer"] is False
    assert data["notifications"] == {
        "count": 1,
        "has_collaborator_activity": True,
        "new_recommendations": 0,
        "unread_private_messages": 0,
        "unread_public_messages": 1,
    }


########################################################################
# patch project details
########################################################################


@pytest.mark.django_db
def test_anonymous_cannot_use_project_patch_api(request, client):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site], status="DRAFT")

    client = APIClient()

    url = reverse("projects-detail", args=[project.id])
    response = client.patch(url, data={"status": "DONE"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_bad_project_is_reported_by_project_patch_api(client):
    user = baker.make(auth_models.User, email="me@example.com")

    client = APIClient()
    client.force_authenticate(user)

    url = reverse("projects-detail", args=[0])
    response = client.patch(url, data={"status": "DONE"})

    assert response.status_code == 404


# XXX Following test returns a 200 and no error on failed processing
# @pytest.mark.django_db
# def test_bad_processing_is_reported_by_project_patch_api(request, client):
#     site = get_current_site(request)
#     user = baker.make(auth_models.User, email="me@example.com")
#     project = baker.make(models.Project, sites=[site], status="DRAFT")
#
#     client = APIClient()
#     client.force_authenticate(user)
#
#     url = reverse("projects-detail", args=[project.id])
#     response = client.patch(url, data={"unknown": "UNKNOWN"})
#
#     assert response.status_code == 400


@pytest.mark.django_db
def test_project_is_updated_by_project_patch_api(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    project = baker.make(models.Project, sites=[site], status="DRAFT")

    utils.assign_advisor(user, project, site)

    new_status = "READY"

    client = APIClient()
    client.force_authenticate(user)

    url = reverse("projects-detail", args=[project.id])
    response = client.patch(url, data={"status": new_status})

    assert response.status_code == 200
    assert response.data["status"] == new_status

    project.refresh_from_db()
    assert project.status == new_status


########################################################################
# user project status list
########################################################################


@pytest.mark.django_db
def test_project_status_needs_authentication():
    client = APIClient()
    url = reverse("userprojectstatus-list")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_change_some_one_else_project_status(request):
    user = baker.make(auth_models.User, email="me@example.com")
    site = get_current_site(request)
    # project and user statuses
    project = baker.make(models.Project, sites=[site])
    baker.make(models.UserProjectStatus, user=user, site=site, project=project)
    baker.make(models.UserProjectStatus, site=site, project=project)
    # FIXME il manque un bout ici ?!?


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
    # a public note with notification for myself
    pub_note = baker.make(models.Note, public=True, project=mine.project)
    verb = "a envoyé un message"
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=pub_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    # a private note with notification for someone else
    priv_note = baker.make(models.Note, public=False, project=mine.project)
    verb = "a envoyé un message dans l'espace conseillers"
    notify.send(
        sender=user,
        recipient=baker.make(auth_models.User),  # for someone else
        verb=verb,
        action_object=priv_note,
        target=project,
        public=False,  # only appear on crm stream
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
    assert first["project"]["is_switchtender"] is True
    assert first["project"]["is_observer"] is False
    assert first["project"]["notifications"] == {
        "count": 1,
        "has_collaborator_activity": True,
        "new_recommendations": 0,
        "unread_private_messages": 0,
        "unread_public_messages": 1,
        "project_id": str(project.id),
    }


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


########################################################################
# user project status detail
########################################################################


@pytest.mark.django_db
def test_project_status_detail_needs_authentication(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])

    client = APIClient()

    url = reverse("userprojectstatus-detail", args=[project.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_status_detail_signals_unknown_object(request):
    user = baker.make(auth_models.User)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("userprojectstatus-detail", args=[0])
    response = client.get(url)

    assert response.status_code == 404


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


########################################################################
# user project status patch
########################################################################


@pytest.mark.django_db
def test_project_status_patch_needs_authentication(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])

    client = APIClient()

    url = reverse("userprojectstatus-detail", args=[project.id])
    response = client.patch(url, data={"status": "DONE"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_status_patch_dont_update_others_object(request):
    user = baker.make(auth_models.User, username="Bob")
    site = get_current_site(request)
    ups = baker.make(models.UserProjectStatus, site=site, status="DRAFT")

    new_status = "DONE"

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-detail", args=[ups.id])
    response = client.patch(url, data={"status": new_status})

    assert response.status_code == 404

    # object is updated
    ups.refresh_from_db()
    assert ups.status == "DRAFT"


@pytest.mark.django_db
def test_project_status_patch_updates_object_and_log(request):
    user = baker.make(auth_models.User, username="Bob")
    site = get_current_site(request)
    ups = baker.make(models.UserProjectStatus, user=user, site=site, status="DRAFT")

    new_status = "DONE"

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-detail", args=[ups.id])
    response = client.patch(url, data={"status": new_status})

    # response is ok with new content
    assert response.status_code == 200
    updated_ups = response.data
    assert updated_ups["status"] == new_status

    # object is updated
    ups.refresh_from_db()
    assert ups.status == new_status

    # update is logged
    stream = user_stream(user, with_user_activity=True)
    assert stream.count() == 1
    assert stream[0].verb == "a changé l'état de son suivi"


########################################################################
# tasks
########################################################################

#
# list tasks


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


#
# update tasks


@pytest.mark.django_db
def test_project_collaborator_can_update_project_task_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=False)

    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-detail", args=[project.id, task.id])
    response = client.patch(url, data={"public": True})

    assert response.status_code == 200

    task.refresh_from_db()
    assert task.public is True


#
# move tasks


@pytest.mark.django_db
def test_non_project_user_cannot_move_project_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, status="READY", sites=[site])
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-move", args=[project.id, tasks[0].id])
    response = client.post(url, data={"above": tasks[1].id})

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_collaborator_cannot_move_unknown_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, status="READY", sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)
    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-move", args=[project.id, task.id])
    response = client.post(url, data={"above": 0})

    assert response.status_code == 404


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
    response = client.post(url, data={"below": tasks[1].id})

    assert response.status_code == 200
    assert response.data == {"status": "insert below done"}


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


########################################################################
# Tasks followups
########################################################################


#
# - get followups for project


@pytest.mark.django_db
def test_project_task_followup_list_closed_to_anonymous_user(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_followup_list_closed_to_user_wo_permission(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_followup_list_returns_followups_to_collaborator(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)
    followup = baker.make(models.TaskFollowup, task=task, status=models.Task.PROPOSED)

    # FIXME here the point should be to state the specific permission
    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1

    first = response.data[0]
    expected_fields = [
        "comment",
        "id",
        "status",
        "status_txt",
        "timestamp",
        "who",
    ]
    assert set(first) == set(expected_fields)
    assert first["id"] == followup.id
    assert first["status"] == followup.status


#
# - create followup for project


@pytest.mark.django_db
def test_project_task_followup_create_closed_to_anonymous_user(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = client.post(url, data={}, format="json")

    assert response.status_code == 403


# FIXME we should have permission checking on followup creation
@pytest.mark.django_db
def test_project_task_followup_create_is_processed_for_auth_user(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    client.force_authenticate(user=user)
    data = {"comment": "a new followup for tasks"}
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = client.post(url, data=data)

    assert response.status_code == 201

    # new followup created
    followups = models.TaskFollowup.objects.filter(task=task)
    assert followups.count() == 1

    followup = followups.first()
    assert followup.status is None  # FIXME should we have a default status ?
    assert followup.comment == data["comment"]

    # returned value
    assert response.data["id"] == followup.id
    assert response.data["comment"] == data["comment"]


#
# - update followup for project


@pytest.mark.django_db
def test_project_task_followup_update_closed_to_anonymous_user(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)
    followup = baker.make(models.TaskFollowup, task=task)

    client = APIClient()
    url = reverse(
        "project-tasks-followups-detail", args=[project.id, task.id, followup.id]
    )
    response = client.post(url, data={}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_followup_update_is_processed_for_auth_user(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)
    followup = baker.make(models.TaskFollowup, task=task)

    # FIXME should use specific permission
    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    data = {"comment": "an updated comment for followup"}
    url = reverse(
        "project-tasks-followups-detail", args=[project.id, task.id, followup.id]
    )
    response = client.patch(url, data=data, format="json")

    assert response.status_code == 200

    # followup updated
    followup.refresh_from_db()
    assert followup.status is None  # FIXME should we have a default status ?
    assert followup.comment == data["comment"]

    # returned value
    assert response.data["id"] == followup.id
    assert response.data["comment"] == data["comment"]


########################################################################
# Tasks notification
########################################################################

#
# fetch notifications


@pytest.mark.django_db
def test_project_task_notifications_list_closed_to_anonymous_user(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    url = reverse("project-tasks-notifications-list", args=[project.id, task.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_notifications_list_returns_notifications_of_advisor(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)

    # a notification on task itself
    notify.send(
        sender=baker.make(auth_models.User),
        recipient=user,
        verb=verbs.Recommendation.CREATED,
        action_object=task,
        target=project,
        private=False,
    )

    # FIXME here the point should be to state the specific permission
    utils.assign_advisor(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-notifications-list", args=[project.id, task.id])
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1

    first = response.data[0]
    expected_fields = [
        "action_object",
        "actor",
        "id",
        "timestamp",
        "verb",
    ]
    assert set(first) == set(expected_fields)


#
# mark all notifications as read


@pytest.mark.django_db
def test_project_task_notifications_mark_read_updates_notifications_of_advisor(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)

    # a notification on task itself
    notify.send(
        sender=baker.make(auth_models.User),
        recipient=user,
        verb=verbs.Recommendation.CREATED,
        action_object=task,
        target=project,
        private=False,
    )

    assert user.notifications.unread().count() == 1

    # FIXME here the point should be to state the specific permission
    utils.assign_advisor(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse(
        "project-tasks-notifications-mark-all-as-read", args=[project.id, task.id]
    )
    response = client.post(url)

    assert response.status_code == 200
    assert response.data == {}
    assert user.notifications.unread().count() == 0


# eof
