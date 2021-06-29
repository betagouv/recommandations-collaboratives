# encoding: utf-8

"""
Tests for project application

authors : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

import pytest

from pytest_django.asserts import assertContains
from pytest_django.asserts import assertNotContains
from pytest_django.asserts import assertRedirects

from django.urls import reverse

import django.core.mail

from django.contrib.auth import models as auth

from model_bakery.recipe import Recipe

from urbanvitaliz.utils import login

from . import models


# TODO when local authority can see & update her project
# TODO check that project, note, and task belong to her

########################################################################
# Landing page
########################################################################


def test_home_page_is_reachable_without_login(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, "UrbanVitaliz")


########################################################################
# Onboarding page
########################################################################


def test_onboarding_page_is_reachable_without_login(client):
    url = reverse("projects-onboarding")
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-onboarding"')


@pytest.mark.django_db
def test_performing_onboarding_create_a_new_project(client):
    with login(client):
        response = client.post(
            reverse("projects-onboarding"),
            data={
                "name": "a project",
                "email": "a@example.com",
                "location": "some place",
                "first_name": "john",
                "last_name": "doe",
                "description": "a project description",
                "impediment": "some impediment",
            },
        )
    project = models.Project.fetch()[0]
    assert project.name == "a project"
    assert response.status_code == 200


########################################################################
# My projects
########################################################################


@pytest.mark.django_db
def test_my_project_not_available_when_not_logged_in(client):
    url = reverse("projects-local-authority")
    response = client.get(url)
    assert response.status_code == 302  # redirects to login


@pytest.mark.django_db
def test_my_projects_are_displayed_on_page(client):
    url = reverse("projects-local-authority")
    with login(client, is_staff=True) as user:
        project = Recipe(models.Project, email=user.email).make()
        response = client.get(url)
    assertContains(response, project.name)
    assert response.status_code == 200


@pytest.mark.django_db
def test_other_projects_are_not_displayed_on_page(client):
    project = Recipe(models.Project, email="other@example.com").make()
    url = reverse("projects-local-authority")
    with login(client, is_staff=True):
        response = client.get(url)
    assertNotContains(response, project.name)
    assert response.status_code == 200


########################################################################
# login
########################################################################


@pytest.mark.django_db
def test_existing_user_receives_email_on_login(client):
    user = Recipe(auth.User, email="jdoe@example.com").make()
    url = reverse("magicauth-login")
    response = client.post(url, data={"email": user.email})
    assert response.status_code == 302
    assert len(django.core.mail.outbox) == 1
    assert user.email in django.core.mail.outbox[0].to


@pytest.mark.django_db
def test_unknown_user_is_created_and_receives_email_on_login(client):
    email = "jdoe@example.com"
    url = reverse("magicauth-login")
    response = client.post(url, data={"email": email})
    assert response.status_code == 302
    assert auth.User.objects.get(email=email)
    assert len(django.core.mail.outbox) == 1
    assert email in django.core.mail.outbox[0].to


########################################################################
# List of projects
########################################################################


@pytest.mark.django_db
def test_project_list_not_available_for_non_staff_users(client):
    url = reverse("projects-project-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_list_available_for_staff_users(client):
    url = reverse("projects-project-list")
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_list_contains_project_name_and_link(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-list")
    with login(client, is_staff=True):
        response = client.get(url)
    detail_url = reverse("projects-project-detail", args=[project.id])
    assertContains(response, detail_url)


########################################################################
# Project details
########################################################################


@pytest.mark.django_db
def test_project_detail_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_detail_available_for_owner(client):
    # project email is same as test user to be logged in
    project = Recipe(models.Project, email="test@example.com").make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, is_staff=False):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_available_for_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_contains_informations(client):
    project = Recipe(models.Project).make()
    task = Recipe(models.Task, project=project).make()
    note = Recipe(models.Note, project=project).make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, is_staff=True):
        response = client.get(url)
    assertContains(response, project.description)
    assertContains(response, task.content)
    assertContains(response, note.content)


@pytest.mark.django_db
def test_project_detail_contains_actions(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, is_staff=True):
        response = client.get(url)
    add_task_url = reverse("projects-create-task", args=[project.id])
    assertContains(response, add_task_url)
    add_note_url = reverse("projects-create-note", args=[project.id])
    assertContains(response, add_note_url)


########################################################################
# update project
########################################################################


@pytest.mark.django_db
def test_update_project_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-update", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_project_available_for_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-update", args=[project.id])
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_project_and_redirect(client):
    project = Recipe(models.Project).make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-update", args=[project.id])
    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "first_name": "john",
        "last_name": "doe",
        "description": "a project description",
        "impediment": "some impediment",
    }

    with login(client, is_staff=True):
        response = client.post(url, data=data)

    project = models.Project.objects.get(id=project.id)
    assert project.name == data["name"]
    assert project.updated_on > updated_on_before

    detail_url = reverse("projects-project-detail", args=[project.id])
    assertRedirects(response, detail_url)


########################################################################
# Project syndication feed
########################################################################


@pytest.mark.django_db
def test_projects_feed_available_for_all_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-feed")
    response = client.get(url)
    detail_url = reverse("projects-project-detail", args=[project.id])
    assertContains(response, detail_url)


########################################################################
# tasks
########################################################################


#
# create


@pytest.mark.django_db
def test_create_task_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-create-task", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_task_available_for_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-create-task", args=[project.id])
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-add-task"')


@pytest.mark.django_db
def test_create_new_task_for_project_and_redirect(client):
    project = Recipe(models.Project).make()
    with login(client, is_staff=True):
        response = client.post(
            reverse("projects-create-task", args=[project.id]),
            data={"content": "this is some content"},
        )
    task = models.Task.fetch()[0]
    assert task.project == project
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
def test_update_task_available_for_staff_users(client):
    task = Recipe(models.Task).make()
    url = reverse("projects-update-task", args=[task.id])
    with login(client, is_staff=True):
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

    with login(client, is_staff=True):
        response = client.post(url, data=data)

    task = models.Task.objects.get(id=task.id)
    assert task.content == data["content"]
    assert task.updated_on > updated_on_before
    assert task.project.updated_on == task.updated_on

    assert response.status_code == 302


########################################################################
# notes
########################################################################


#
# create


@pytest.mark.django_db
def test_create_note_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-create-note", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_note_available_for_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-create-note", args=[project.id])
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-add-note"')


@pytest.mark.django_db
def test_create_new_note_for_project_and_redirect(client):
    project = Recipe(models.Project).make()
    with login(client, is_staff=True):
        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content"},
        )
    note = models.Note.fetch()[0]
    assert note.project == project
    assert response.status_code == 302


#
# update


@pytest.mark.django_db
def test_update_note_not_available_for_non_staff_users(client):
    note = Recipe(models.Note).make()
    url = reverse("projects-update-note", args=[note.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_note_available_for_staff_users(client):
    note = Recipe(models.Note).make()
    url = reverse("projects-update-note", args=[note.id])
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200
    # FIXME rename add-note to edit-note ?
    assertContains(response, 'form id="form-projects-add-note"')


@pytest.mark.django_db
def test_update_note_for_project_and_redirect(client):
    note = Recipe(models.Note).make()
    updated_on_before = note.updated_on
    url = reverse("projects-update-note", args=[note.id])
    data = {"content": "this is some content"}

    with login(client, is_staff=True):
        response = client.post(url, data=data)

    note = models.Note.objects.get(id=note.id)
    assert note.content == data["content"]
    assert note.updated_on > updated_on_before
    assert note.project.updated_on == note.updated_on

    assert response.status_code == 302


########################################################################
# pushing a resource to a project's owner
########################################################################


@pytest.mark.django_db
def test_staff_push_resource_to_project(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-push-resource", args=[project.id])
    with login(client, is_staff=True):
        response = client.post(url)
    # project is stored in session and user redirected to resource app.
    assert client.session["project_id"] == project.id
    newurl = reverse("resources-resource-search")
    assertRedirects(response, newurl)


# eof
