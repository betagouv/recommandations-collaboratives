# encoding: utf-8

"""
Tests for project application

authors : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

from contextlib import contextmanager

import pytest

from pytest_django.asserts import assertContains

from django.urls import reverse

import django.core.mail

from django.contrib.auth import models as auth

from model_bakery.recipe import Recipe

from . import models


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


########################################################################
# login
########################################################################


@pytest.mark.django_db
def test_existing_user_receives_email_on_login(client, mocker):
    mocker.patch("django.core.mail.send_mail")
    user = Recipe(auth.User, email="jdoe@example.com").make()
    url = reverse("magicauth-login")
    response = client.post(url, data={"email": user.email})
    assert response.status_code == 302
    django.core.mail.send_mail.assert_called_once()


@pytest.mark.xfail  # FIXME make this test pass
@pytest.mark.django_db
def test_unknown_user_is_created_and_receives_email_on_login(client, mocker):
    mocker.patch("django.core.mail.send_mail")
    email = "jdoe@example.com"
    url = reverse("magicauth-login")
    response = client.post(url, data={"email": email})
    assert response.status_code == 302
    assert auth.User.objects.get(email=email)
    django.core.mail.send_mail.assert_called_once()


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
# create task
########################################################################


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


########################################################################
# create note
########################################################################


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


########################################################################
# Helpers
########################################################################


@contextmanager
def login(client, is_staff=False):
    """Create a user and sign her into the application"""
    user = Recipe(auth.User, is_staff=is_staff).make()
    client.force_login(user)
    yield user


# eof
