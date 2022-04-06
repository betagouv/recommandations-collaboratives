# encoding: utf-8

"""
Tests for project application, tasks

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""


import pytest
from django.contrib.auth import models as auth
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertRedirects
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.resources import models as resources
from urbanvitaliz.apps.survey import models as survey_models
from urbanvitaliz.utils import login

from .. import models

########################################################################
# Task Recommendation
########################################################################


@pytest.mark.django_db
def test_task_recommendation_list_not_available_for_non_staff(client):
    url = reverse("projects-task-recommendation-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_task_recommendation_list_available_for_staff(client):
    url = reverse("projects-task-recommendation-list")
    with login(client, is_staff=True):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_task_recommendation_create_not_available_for_non_staff(client):
    url = reverse("projects-task-recommendation-create")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_task_recommendation_available_for_staff(client):
    url = reverse("projects-task-recommendation-create")
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_recommendation_is_created(client):
    url = reverse("projects-task-recommendation-create")
    resource = Recipe(resources.Resource).make()

    data = {"text": "mew", "resource": resource.pk}
    with login(client, is_staff=True):
        response = client.post(url, data=data)

    assert models.TaskRecommendation.objects.count() == 1

    assert response.status_code == 302
    newurl = reverse("projects-task-recommendation-list")
    assertRedirects(response, newurl)


@pytest.mark.django_db
def test_task_recommendation_update_not_available_for_non_staff(client):
    recommendation = Recipe(models.TaskRecommendation).make()
    url = reverse("projects-task-recommendation-update", args=(recommendation.pk,))
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_task_recommendation_update_available_for_staff(client):
    recommendation = Recipe(models.TaskRecommendation).make()
    url = reverse("projects-task-recommendation-update", args=(recommendation.pk,))
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_recommendation_is_updated(client):
    recommendation = Recipe(models.TaskRecommendation).make()

    url = reverse("projects-task-recommendation-update", args=(recommendation.pk,))

    data = {"text": "new-text", "resource": recommendation.resource.pk}
    with login(client, is_staff=True):
        response = client.post(url, data=data)

    assert response.status_code == 302
    newurl = reverse("projects-task-recommendation-list")
    assertRedirects(response, newurl)

    assert models.TaskRecommendation.objects.count() == 1
    updated_recommendation = models.TaskRecommendation.objects.all()[0]
    assert updated_recommendation.text == data["text"]


@pytest.mark.django_db
def test_task_suggestion_not_available_for_non_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_task_suggestion_when_no_survey(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_suggestion_available_with_bare_project(client):
    Recipe(survey_models.Survey, pk=1).make()
    Recipe(models.TaskRecommendation, condition="").make()
    project = Recipe(models.Project).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_suggestion_available_with_filled_project(client):
    Recipe(survey_models.Survey, pk=1).make()
    commune = Recipe(geomatics.Commune).make()
    Recipe(models.TaskRecommendation, condition="").make()
    project = Recipe(models.Project, commune=commune).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_suggestion_available_with_localized_reco(client):
    Recipe(survey_models.Survey, pk=1).make()
    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()
    Recipe(
        models.TaskRecommendation,
        condition="",
        departments=[
            dept,
        ],
    ).make()
    project = Recipe(models.Project, commune=commune).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


#
# Visit


@pytest.mark.django_db
def test_visit_task_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=False, resource=None).make()
    with login(client, email=owner_email):
        response = client.get(
            reverse("projects-visit-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.visited is True
    assert response.status_code == 302


@pytest.mark.django_db
def test_visit_task_for_project_and_redirect_to_resource_for_project_owner(client):
    owner_email = "owner@univer.se"
    resource = resources.Resource()
    resource.save()

    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=False, resource=resource).make()
    with login(client, email=owner_email):
        response = client.get(
            reverse("projects-visit-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.visited is True
    assert response.status_code == 302


#
# mark as done
@pytest.mark.django_db
def test_new_task_toggle_done_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(
        models.Task, status=models.Task.PROPOSED, project=project, visited=True
    ).make()
    with login(client, email=owner_email):
        response = client.post(
            reverse("projects-toggle-done-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.status == models.Task.DONE
    assert response.status_code == 302


@pytest.mark.django_db
def test_done_task_toggle_done_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(
        models.Task, project=project, visited=True, status=models.Task.DONE
    ).make()

    with login(client, email=owner_email):
        response = client.post(
            reverse("projects-toggle-done-task", args=[task.id]),
        )

    task = models.Task.objects.all()[0]
    assert task.status == models.Task.PROPOSED
    assert response.status_code == 302


@pytest.mark.django_db
def test_refuse_task_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=False).make()
    with login(client, email=owner_email):
        response = client.post(
            reverse("projects-refuse-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.status == models.Task.NOT_INTERESTED
    assert response.status_code == 302


def test_already_done_task_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=False).make()
    with login(client, email=owner_email):
        response = client.post(
            reverse("projects-already-done-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.status == models.Task.ALREADY_DONE
    assert response.status_code == 302


#
# update


@pytest.mark.django_db
def test_update_task_not_available_for_non_staff_users(client):
    task = Recipe(models.Task).make()
    url = reverse("projects-update-task", args=[task.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_task_available_for_switchtender(client):
    task = Recipe(models.Task).make()
    url = reverse("projects-update-task", args=[task.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200
    # FIXME rename add-task to edit-task ?
    assertContains(response, 'form id="form-projects-add-task"')


@pytest.mark.django_db
def test_update_task_for_project_and_redirect(client):
    task = Recipe(models.Task).make()
    updated_on_before = task.updated_on
    url = reverse("projects-update-task", args=[task.id])
    data = {"content": "this is some content"}

    with login(client, groups=["switchtender"]):
        response = client.post(url, data=data)

    task = models.Task.objects.get(id=task.id)
    assert task.content == data["content"]
    assert task.updated_on > updated_on_before
    assert task.project.updated_on == task.updated_on

    assert response.status_code == 302


#
# delete


@pytest.mark.django_db
def test_delete_task_not_available_for_non_staff_users(client):
    task = Recipe(models.Task).make()
    url = reverse("projects-delete-task", args=[task.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_task_from_project_and_redirect(client):
    task = Recipe(models.Task).make()
    with login(client, groups=["switchtender"]):
        response = client.post(reverse("projects-delete-task", args=[task.id]))
    task = models.Task.deleted_objects.get(id=task.id)
    assert task.deleted
    assert response.status_code == 302


########################################################################
# Push Actions
########################################################################

########################################################################
# Task Notifications
########################################################################


@pytest.mark.django_db
def test_create_new_task_for_project_notify_collaborators(mocker, client):
    owner = Recipe(auth.User, username="owner", email="owner@example.com").make()

    project = Recipe(models.Project, status="READY", emails=[owner.email]).make()
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)

        client.post(
            reverse("projects-project-create-action", args=[project.id]),
            data={
                "push_type": "noresource",
                "intent": "yeah",
                "content": "this is some content",
                "public": True,
            },
        )

    assert owner.notifications.count() == 1


@pytest.mark.django_db
def test_task_update_does_not_trigger_notifications(client):
    owner = Recipe(auth.User, username="owner", email="owner@example.com").make()
    project = Recipe(models.Project, status="READY", emails=[owner.email]).make()

    task = Recipe(models.Task, project=project, public=True).make()

    url = reverse("projects-update-task", args=(task.pk,))

    data = {"text": "new-text"}
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        response = client.post(url, data=data)

    assert response.status_code == 302
    assert owner.notifications.count() == 0


@pytest.mark.django_db
def test_create_task_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-create-action", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_task_available_for_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-create-action", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)

        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_create_new_action_with_invalid_push_type(client):
    project = Recipe(models.Project).make()

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)

        client.post(
            reverse("projects-project-create-action", args=[project.id]),
            data={
                "push_type": "blah",
                "public": True,
            },
        )
    assert models.Task.objects.count() == 0


@pytest.mark.django_db
def test_create_new_action_as_draft(client):
    project = Recipe(models.Project).make()

    intent = "My Intent"
    content = "My Content"

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)

        response = client.post(
            reverse("projects-project-create-action", args=[project.id]),
            data={
                "push_type": "noresource",
                "intent": intent,
                "content": content,
            },
        )
    task = models.Task.objects.all()[0]
    assert task.public is False
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_new_action_without_resource(client):
    project = Recipe(models.Project).make()

    intent = "My Intent"
    content = "My Content"

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)

        response = client.post(
            reverse("projects-project-create-action", args=[project.id]),
            data={
                "push_type": "noresource",
                "public": True,
                "intent": intent,
                "content": content,
            },
        )
    task = models.Task.objects.all()[0]
    assert task.project == project
    assert task.content == content
    assert task.public is True
    assert task.intent == intent
    assert task.resource is None
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_new_action_with_single_resource(client):
    project = Recipe(models.Project).make()
    resource = Recipe(resources.Resource, status=resources.Resource.PUBLISHED).make()

    intent = "My Intent"
    content = "My Content"

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)

        response = client.post(
            reverse("projects-project-create-action", args=[project.id]),
            data={
                "push_type": "single",
                "public": True,
                "resource": resource.pk,
                "intent": intent,
                "content": content,
            },
        )
    task = models.Task.objects.first()
    assert task
    assert task.project == project
    assert task.public is True
    assert task.resource == resource
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_new_action_with_multiple_resources(client):
    project = Recipe(models.Project).make()
    resource1 = Recipe(resources.Resource, status=resources.Resource.PUBLISHED).make()
    resource2 = Recipe(resources.Resource, status=resources.Resource.PUBLISHED).make()

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)

        response = client.post(
            reverse("projects-project-create-action", args=[project.id]),
            data={
                "push_type": "multiple",
                "public": True,
                "resources": [resource1.pk, resource2.pk],
            },
        )
    assert models.Task.objects.count() == 2

    for task in models.Task.objects.all():
        assert task.project == project
        assert task.public is True

    assert response.status_code == 302


################################################################################
# Task Followups
################################################################################


@pytest.mark.django_db
def test_update_task_followup_not_available_for_non_creator(client):
    followup = Recipe(models.TaskFollowup).make()
    url = reverse("projects-task-followup-update", args=[followup.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_task_followup_accesible_by_creator(client):
    with login(client) as user:
        followup = Recipe(models.TaskFollowup, who=user, status=0).make()
        url = reverse("projects-task-followup-update", args=[followup.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_task_followup_by_creator(client):
    data = {"comment": "hello"}

    with login(client) as user:
        followup = Recipe(models.TaskFollowup, status=0, who=user).make()
        url = reverse("projects-task-followup-update", args=[followup.id])
        response = client.post(url, data=data)

    followup = models.TaskFollowup.objects.get(pk=followup.pk)
    assert followup.comment == data["comment"]
    assert response.status_code == 302
