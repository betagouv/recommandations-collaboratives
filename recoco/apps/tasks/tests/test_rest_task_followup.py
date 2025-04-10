import pytest
from django.contrib.auth import models as auth_models
from django.urls import reverse
from model_bakery import baker

from recoco.apps.addressbook.models import Contact
from recoco.apps.projects import utils

from .. import models


@pytest.mark.django_db
def test_project_task_followup_list_closed_to_anonymous_user(
    api_client, current_site, project
):
    task = baker.make(models.Task, project=project, site=current_site, public=True)

    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = api_client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_followup_list_closed_to_user_wo_permission(
    api_client, current_site, project
):
    user = baker.make(auth_models.User)
    task = baker.make(models.Task, project=project, site=current_site, public=True)

    api_client.force_authenticate(user=user)
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = api_client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_followup_list_closed_for_dissociate_task_and_project(
    api_client, current_site, project, make_project
):
    user = baker.make(auth_models.User)
    project1 = project
    _ = baker.make(models.Task, project=project1, site=current_site, public=True)
    utils.assign_advisor(user, project1)

    project2 = make_project(site=current_site)
    task2 = baker.make(models.Task, project=project2, site=current_site, public=True)
    _ = baker.make(models.TaskFollowup, task=task2, status=models.Task.PROPOSED)

    api_client.force_authenticate(user=user)
    url = reverse("project-tasks-followups-list", args=[project1.id, task2.id])
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_project_task_followup_list_returns_followups_to_collaborator(
    api_client, current_site, project
):
    user = baker.make(auth_models.User)
    task = baker.make(models.Task, project=project, site=current_site, public=True)
    followup = baker.make(models.TaskFollowup, task=task, status=models.Task.PROPOSED)

    utils.assign_collaborator(user, project)

    api_client.force_authenticate(user=user)
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1

    first = response.data[0]
    expected_fields = [
        "comment",
        "contact",
        "id",
        "status",
        "status_txt",
        "timestamp",
        "who",
    ]
    assert set(first) == set(expected_fields)
    assert first["id"] == followup.id
    assert first["status"] == followup.status


@pytest.mark.django_db
def test_project_task_followup_create_closed_to_anonymous_user(
    api_client, current_site, project
):
    task = baker.make(models.Task, project=project, site=current_site, public=True)

    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = api_client.post(url, data={}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_followup_create_not_allowed_for_simple_auth_user(
    api_client, current_site, project
):
    user = baker.make(auth_models.User)
    task = baker.make(models.Task, project=project, site=current_site, public=True)

    api_client.force_authenticate(user=user)
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = api_client.post(url, data={"comment": "a new followup for tasks"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_followup_create_is_processed_for_auth_user(
    api_client, current_site, project
):
    user = baker.make(auth_models.User)
    task = baker.make(models.Task, project=project, site=current_site, public=True)
    contact = baker.make(Contact)

    api_client.force_authenticate(user=user)
    utils.assign_advisor(user, project)

    data = {
        "comment": "a new followup for tasks",
        "contact": contact.id,
    }
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = api_client.post(url, data=data)

    assert response.status_code == 201

    # new followup created
    followups = models.TaskFollowup.objects.filter(task_id=task.id)
    assert followups.count() == 1
    followup = followups.first()
    assert followup.status is None  # FIXME should we have a default status ?
    assert followup.comment == "a new followup for tasks"
    assert followup.contact_id == contact.id
    assert followup.who_id == user.id

    # returned value
    assert response.data == {
        "id": followup.id,
        "status": None,
        "comment": "a new followup for tasks",
        "contact": contact.id,
        "who": user.id,
        "task": task.id,
    }


@pytest.mark.django_db
def test_project_task_followup_update_closed_to_anonymous_user(
    api_client, current_site, project
):
    task = baker.make(models.Task, project=project, site=current_site, public=True)
    followup = baker.make(models.TaskFollowup, task=task)

    url = reverse(
        "project-tasks-followups-detail", args=[project.id, task.id, followup.id]
    )
    response = api_client.post(url, data={}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_followup_update_is_processed_for_auth_user(
    api_client, current_site, project
):
    user = baker.make(auth_models.User)
    task = baker.make(models.Task, project=project, site=current_site, public=True)
    contact = baker.make(Contact)
    followup = baker.make(
        models.TaskFollowup, task=task, contact=contact, comment="my comment"
    )

    api_client.force_authenticate(user=user)
    utils.assign_advisor(user, project)

    new_comment = "my new comment"
    new_contact = baker.make(Contact)

    url = reverse(
        "project-tasks-followups-detail", args=[project.id, task.id, followup.id]
    )
    response = api_client.patch(
        url,
        data={
            "comment": new_comment,
            "contact": new_contact.id,
        },
        format="json",
    )

    assert response.status_code == 200

    # followup updated
    followup.refresh_from_db()
    assert followup.status is None  # FIXME should we have a default status ?
    assert followup.comment == new_comment
    assert followup.contact == new_contact

    # returned value
    assert response.data["id"] == followup.id
    assert response.data["comment"] == new_comment
    assert response.data["contact"] == new_contact.id
