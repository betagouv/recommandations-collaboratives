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
from notifications.signals import notify
from rest_framework.test import APIClient

from urbanvitaliz.utils import login
from urbanvitaliz import verbs
from urbanvitaliz.apps.projects import models as project_models
from urbanvitaliz.apps.resources import models as resource_models

from urbanvitaliz.apps.projects import utils

from .. import models


########################################################################
# tasks
########################################################################

#
# list tasks


@pytest.mark.django_db
def test_project_collaborator_can_see_project_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(project_models.Project, sites=[site])
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
def test_task_includes_resource_content_bug_fix(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(project_models.Project, sites=[site])
    resource = baker.make(resource_models.Resource, sites=[site])
    baker.make(
        models.Task, project=project, resource=resource, site=site, public=True
    )
    utils.assign_observer(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200

    task = response.data[0]
    assert task["resource"] is not None


@pytest.mark.django_db
def test_project_observer_can_see_project_tasks_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, status="READY", sites=[site])
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
    project = baker.make(project_models.Project, status="READY", sites=[site])
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
    project = baker.make(project_models.Project, status="READY", sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_followup_list_closed_to_user_wo_permission(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
    task = baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    url = reverse("project-tasks-notifications-list", args=[project.id, task.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_notifications_list_returns_notifications_of_advisor(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    project = baker.make(project_models.Project, sites=[site])
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
    project = baker.make(project_models.Project, sites=[site])
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
