# encoding: utf-8

"""
kTests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from notifications.signals import notify
from rest_framework.test import APIClient

from recoco import verbs
from recoco.apps.addressbook.models import Contact
from recoco.apps.projects import utils
from recoco.apps.resources.models import Resource
from recoco.utils import login

from .. import models

########################################################################
# tasks
########################################################################

#
# list tasks


@pytest.mark.django_db
def test_project_collaborator_can_see_project_tasks_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200
    assert set(e["id"] for e in response.data) == set(t.id for t in tasks)


@pytest.mark.django_db
def test_task_includes_resource_content_bug_fix(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    resource = baker.make(Resource, sites=[site])
    baker.make(models.Task, project=project, resource=resource, site=site, public=True)
    utils.assign_observer(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200

    task = response.data[0]
    assert task["resource"] is not None


@pytest.mark.django_db
def test_project_observer_can_see_project_tasks_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )

    utils.assign_observer(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200
    assert set(e["id"] for e in response.data) == set(t.id for t in tasks)


@pytest.mark.django_db
def test_regional_actor_can_see_project_tasks_for_site(request, project):
    user = baker.make(auth_models.User)

    site = get_current_site(request)

    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    utils.assign_observer(user, project, site)

    client = APIClient()
    with login(client, groups=["example_com_advisor"]) as user:
        url = reverse("project-tasks-list", args=[project.id])
        response = client.get(url)

    assert response.status_code == 200
    assert set(e["id"] for e in response.data) == set(t.id for t in tasks)


@pytest.mark.django_db
def test_project_advisor_can_see_project_tasks_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    utils.assign_advisor(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200
    assert set(e["id"] for e in response.data) == set(t.id for t in tasks)


@pytest.mark.django_db
def test_user_cannot_see_project_tasks_when_not_in_relation(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = client.get(url)

    assert response.status_code == 403


#
# create task


@pytest.mark.django_db
def test_project_simple_user_cannot_create_project_task(api_client, project):
    user = baker.make(auth_models.User)
    api_client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = api_client.post(url, data={"order": 0})
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_collaborator_cannot_create_project_task_for_site(api_client, project):
    user = baker.make(auth_models.User)
    utils.assign_collaborator(user, project)
    api_client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])
    response = api_client.post(url, data={"order": 0})
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_advisor_can_create_project_task_for_site(
    api_client, current_site, project
):
    user = baker.make(auth_models.User)
    utils.assign_advisor(user, project)
    api_client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])

    contact = baker.make(Contact, site=current_site)
    resource = baker.make(Resource, sites=[current_site])

    data = {
        "status": 1,
        "visited": False,
        "public": True,
        "priority": 9,
        "order": 0,
        "intent": "the intent",
        "content": "the content",
        "contact_id": contact.id,
        "resource_id": resource.id,
    }
    response = api_client.post(url, data=data)
    assert response.status_code == 201

    created_task = models.Task.objects.filter(project=project).first()
    assert created_task.site == current_site
    assert created_task.project == project
    assert created_task.created_by == user
    assert created_task.intent == data["intent"]
    assert created_task.contact == contact
    assert created_task.resource == resource


@pytest.mark.django_db
def test_project_advisor_can_create_project_task_for_site_no_content(
    api_client, current_site, project
):
    user = baker.make(auth_models.User)
    utils.assign_advisor(user, project)
    api_client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])

    data = {
        "status": 1,
        "visited": False,
        "public": True,
        "priority": 9,
        "order": 0,
        "intent": "the intent",
        "content": "",
    }
    response = api_client.post(url, data=data)
    assert response.status_code == 201

    created_task = models.Task.objects.filter(project=project).first()
    assert created_task.site == current_site
    assert created_task.project == project
    assert created_task.created_by == user
    assert created_task.intent == data["intent"]
    assert created_task.content == data["content"]


@pytest.mark.django_db
def test_cannot_create_project_task_for_site_invalid_contact_or_resource(
    api_client, project
):
    user = baker.make(auth_models.User)
    utils.assign_advisor(user, project)
    api_client.force_authenticate(user=user)
    url = reverse("project-tasks-list", args=[project.id])

    contact = baker.make(Contact)
    response = api_client.post(url, data={"order": 1, "contact_id": contact.id})
    assert response.status_code == 400
    assert "contact_id" in response.data.keys()

    resource = baker.make(Resource)
    response = api_client.post(url, data={"order": 1, "resource_id": resource.id})
    assert response.status_code == 400
    assert "resource_id" in response.data.keys()


#
# update tasks


@pytest.mark.django_db
def test_project_advisor_cannot_update_other_project_task_for_site(
    request, project, make_project
):
    user = baker.make(auth_models.User)
    site = get_current_site(request)

    # to test object level perm, user is collaborator on an other project
    other_project = make_project(site=site)
    utils.assign_advisor(user, other_project)

    task = baker.make(models.Task, project=project, site=site, public=False)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-detail", args=[project.id, task.id])
    response = client.patch(url, data={"public": True})

    assert response.status_code == 403

    task.refresh_from_db()
    assert task.public is False


@pytest.mark.django_db
def test_project_collaborator_cannot_update_project_task_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(models.Task, project=project, site=site, public=False)

    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-detail", args=[project.id, task.id])
    response = client.patch(url, data={"public": True})

    assert response.status_code == 403

    task.refresh_from_db()
    assert task.public is False


@pytest.mark.django_db
def test_project_advisor_can_update_project_task_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(models.Task, project=project, site=site, public=False)

    utils.assign_advisor(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-detail", args=[project.id, task.id])
    response = client.patch(url, data={"public": True})

    assert response.status_code == 200

    task.refresh_from_db()
    assert task.public is True


@pytest.mark.django_db
def test_project_advisor_can_update_project_task_for_site_no_content(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(
        models.Task, project=project, site=site, public=False, content="blabla"
    )

    utils.assign_advisor(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-detail", args=[project.id, task.id])
    response = client.patch(url, data={"content": ""})

    assert response.status_code == 200

    task.refresh_from_db()
    assert task.content == ""


##################
# mark task as visited
##################
@pytest.mark.django_db
def test_project_collaborator_can_mark_task_as_visited(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(
        models.Task, project=project, site=site, public=True, visited=False
    )

    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-mark-visited", args=[project.id, task.id])
    response = client.post(url)

    assert response.status_code == 204

    task.refresh_from_db()
    assert task.visited is True


@pytest.mark.django_db
def test_project_collaborator_cannot_mark_task_as_visited_if_draft(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(
        models.Task, project=project, site=site, public=False, visited=False
    )

    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-mark-visited", args=[project.id, task.id])
    response = client.post(url)

    assert response.status_code == 403

    task.refresh_from_db()
    assert task.visited is False


@pytest.mark.django_db
def test_project_hijacked_collaborator_cannot_mark_task_as_visited(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(
        models.Task, project=project, site=site, public=True, visited=False
    )

    utils.assign_collaborator(user, project)

    client = APIClient()
    user.is_hijacked = True
    client.force_authenticate(user=user)
    url = reverse("project-tasks-mark-visited", args=[project.id, task.id])
    response = client.post(url)

    assert response.status_code == 304

    task.refresh_from_db()
    assert task.visited is False


@pytest.mark.django_db
def test_project_task_not_marked_as_visited_if_not_collaborator(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(
        models.Task, project=project, site=site, public=True, visited=False
    )

    utils.assign_advisor(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-mark-visited", args=[project.id, task.id])
    response = client.post(url)

    assert response.status_code == 304

    task.refresh_from_db()
    assert task.visited is False


#
# move tasks


@pytest.mark.django_db
def test_non_project_user_cannot_move_project_tasks_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-move", args=[project.id, tasks[0].id])
    response = client.post(url, data={"above": tasks[1].id})

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_advisor_cannot_move_unknown_tasks_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(models.Task, project=project, site=site, public=True)
    utils.assign_advisor(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-move", args=[project.id, task.id])
    response = client.post(url, data={"above": 0})

    assert response.status_code == 404


@pytest.mark.django_db
def test_project_collaborator_can_move_project_tasks_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
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
def test_project_observer_can_move_project_tasks_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
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
def test_project_observer_can_move_project_task_to_top(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    utils.assign_observer(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-move", args=[project.id, tasks[1].id])
    response = client.post(url, data={"top": True})

    assert response.status_code == 200
    assert response.data == {"status": "insert top done"}


@pytest.mark.django_db
def test_project_observer_can_move_project_task_to_bottom(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    tasks = baker.make(
        models.Task, project=project, site=site, public=True, _quantity=2
    )
    utils.assign_observer(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("project-tasks-move", args=[project.id, tasks[0].id])
    response = client.post(url, data={"bottom": True})

    assert response.status_code == 200
    assert response.data == {"status": "insert bottom done"}


@pytest.mark.django_db
def test_project_advisor_can_move_project_tasks_for_site(request, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
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
# Tasks notification
########################################################################

#
# fetch notifications


@pytest.mark.django_db
def test_project_task_notifications_list_closed_to_anonymous_user(request, project):
    site = get_current_site(request)
    task = baker.make(models.Task, project=project, site=site, public=True)

    client = APIClient()
    url = reverse("project-tasks-notifications-list", args=[project.id, task.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_task_notifications_list_returns_notifications_of_advisor(
    request, project
):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
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
def test_project_task_notifications_mark_read_updates_notifications_of_advisor(
    request, project
):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
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


# -- recommendations


@pytest.mark.django_db
def test_unassigned_switchtender_should_see_recommendations(request):
    site = get_current_site(request)
    task = baker.make(models.Task, site=site, project__sites=[site])

    client = APIClient()

    with login(client) as user:
        utils.assign_advisor(user, task.project)

        url = reverse("project-tasks-list", args=[task.project.id])
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_unassigned_user_should_not_see_recommendations(request):
    site = get_current_site(request)
    task = baker.make(models.Task, site=site, project__sites=[site])

    client = APIClient()

    with login(client):
        url = reverse("project-tasks-list", args=[task.project.id])
        response = client.get(url)

    assert response.status_code == 403


#################################################################
# Activity flags
#################################################################
@pytest.mark.django_db
def test_last_members_activity_is_updated_by_member_followup_via_rest(
    request, client, project
):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(models.Task, project=project, site=site, public=True)

    utils.assign_collaborator(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    utils.assign_advisor(user, project)
    data = {"comment": "an updated comment for followup"}
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    before_update = timezone.now()
    response = client.post(url, data=data, format="json")

    assert response.status_code == 201

    project.refresh_from_db()

    assert project.last_members_activity_at > before_update


@pytest.mark.django_db
def test_last_members_activity_not_updated_by_advisor_followup_via_rest(
    request, client, project
):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    task = baker.make(models.Task, project=project, site=site, public=True)

    utils.assign_advisor(user, project)

    client = APIClient()
    client.force_authenticate(user=user)
    data = {"comment": "an updated comment for followup"}
    url = reverse("project-tasks-followups-list", args=[project.id, task.id])
    before_update = timezone.now()
    response = client.post(url, data=data, format="json")

    assert response.status_code == 201

    project.refresh_from_db()

    assert project.last_members_activity_at < before_update


# eof
