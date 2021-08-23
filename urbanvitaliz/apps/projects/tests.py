# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

import django.core.mail
import pytest
from django.contrib.auth import models as auth
from django.contrib.messages import get_messages
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.resources import models as resources
from urbanvitaliz.utils import login

from . import models
from .templatetags import projects_extra

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
                "impediments": "some impediment",
            },
        )
    project = models.Project.fetch()[0]
    assert project.name == "a project"
    assert project.is_draft
    note = models.Note.objects.all()[0]
    assert note.project == project
    assert note.content == f"# Demande initiale\n\n{project.impediments}"
    assert response.status_code == 302


@pytest.mark.django_db
def test_performing_onboarding_sets_existing_postal_code(client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    with login(client):
        response = client.post(
            reverse("projects-onboarding"),
            data={
                "name": "a project",
                "email": "a@example.com",
                "location": "some place",
                "first_name": "john",
                "last_name": "doe",
                "postcode": commune.postal,
                "description": "a project description",
                "impediments": "some impediment",
            },
        )
    assert response.status_code == 302
    project = models.Project.fetch()[0]
    assert project.commune == commune


@pytest.mark.django_db
def test_performing_onboarding_discard_unknown_postal_code(client):
    with login(client):
        response = client.post(
            reverse("projects-onboarding"),
            data={
                "name": "a project",
                "email": "a@example.com",
                "location": "some place",
                "first_name": "john",
                "last_name": "doe",
                "postcode": "12345",
                "description": "a project description",
                "impediments": "some impediment",
            },
        )
    assert response.status_code == 302
    project = models.Project.fetch()[0]
    assert project.commune is None


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
    with login(client, is_staff=False) as user:
        project = Recipe(models.Project, email=user.email).make()
        response = client.get(url)
    # template does a capfirst that capitalize the first word of title
    assertContains(response, project.name.capitalize()[:20])  # truncated name
    assert response.status_code == 200


@pytest.mark.django_db
def test_my_projects_are_stored_in_session(client):
    url = reverse("projects-local-authority")
    with login(client, is_staff=False) as user:
        project = Recipe(models.Project, email=user.email).make()
        client.get(url)
    assert len(client.session["projects"]) == 1
    session_project = client.session["projects"][0]
    assert session_project["id"] == project.id


@pytest.mark.django_db
def test_other_projects_are_not_displayed_on_page(client):
    project = Recipe(models.Project, email="other@example.com").make()
    url = reverse("projects-local-authority")
    with login(client, is_staff=False):
        response = client.get(url)
    assertNotContains(response, project.name)
    assert response.status_code == 200


@pytest.mark.django_db
def test_other_projects_are_not_stored_in_session(client):
    project = Recipe(models.Project, email="other@exmaple.com").make()
    url = reverse("projects-local-authority")
    with login(client, is_staff=False):
        client.get(url)
    assert {"name": project.name, "id": project.id} not in client.session["projects"]


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
# accept project
########################################################################


@pytest.mark.django_db
def test_accept_project_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-accept", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_accept_project_and_redirect(client):
    project = Recipe(models.Project).make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-accept", args=[project.id])

    with login(client, is_staff=True):
        response = client.post(url)

    project = models.Project.objects.get(id=project.id)
    assert not project.is_draft
    assert project.updated_on > updated_on_before

    detail_url = reverse("projects-project-detail", args=[project.id])
    assertRedirects(response, detail_url)


########################################################################
# delete project
########################################################################


@pytest.mark.django_db
def test_delete_project_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-delete", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_project_and_redirect(client):
    project = Recipe(models.Project).make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-delete", args=[project.id])

    with login(client, is_staff=True):
        response = client.post(url)

    project = models.Project.objects.get(id=project.id)
    assert project.deleted
    assert project.updated_on > updated_on_before

    list_url = reverse("projects-project-list")
    assertRedirects(response, list_url)


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
    with login(client, is_staff=True):
        response = client.post(reverse("projects-delete-task", args=[task.id]))
    task = models.Task.deleted_objects.get(id=task.id)
    assert task.deleted
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


@pytest.mark.django_db
def test_private_note_shown_only_to_staff(client):
    user_email = "not@admin.here"
    note_content = "this is a private note"
    project = Recipe(models.Project, email=user_email).make()
    with login(client, is_staff=True):
        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": note_content},
        )

    with login(client, username="project_owner", email=user_email, is_staff=False):
        response = client.get(project.get_absolute_url())

    assertNotContains(response, note_content)


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


@pytest.mark.django_db
def test_delete_note_for_project_and_redirect(client):
    project = Recipe(models.Project).make()
    note = Recipe(models.Note, project=project).make()
    url = reverse("projects-delete-note", args=[note.id])

    with login(client, is_staff=True):
        response = client.post(url)

    note = models.Note.objects.get(id=note.id)
    assert note.deleted is not None

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


@pytest.mark.django_db
def test_staff_push_resource_to_project_needs_project_id(client):
    project = Recipe(models.Project).make()
    resource = Recipe(resources.Resource, public=True).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, is_staff=True):
        session = client.session
        session["project_id"] = project.id
        session.save()
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_staff_push_resource_to_project_fails_if_no_project_in_session(client):
    resource = Recipe(resources.Resource, public=True).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, is_staff=True):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_staff_create_action_for_resource_push(client):
    project = Recipe(models.Project).make()
    resource = Recipe(resources.Resource, public=True).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, is_staff=True):
        # project_id should be in session
        session = client.session
        session["project_id"] = project.id
        session.save()
        data = {"intent": "read this", "content": "some nice content"}
        response = client.post(url, data=data)

    # a new Recommmendation is created
    task = models.Task.objects.all()[0]
    assert task.project == project
    assert task.resource == resource
    assert task.content == data["content"]
    assert task.intent == data["intent"]
    # user is redirected to poject
    newurl = reverse("projects-project-detail", args=[project.id])
    assertRedirects(response, newurl)
    # sessions is cleaned up
    assert "project_id" not in client.session


@pytest.mark.django_db
def test_staff_create_action_for_resource_push_with_notification(client):
    project = Recipe(models.Project).make()
    resource = Recipe(resources.Resource, public=True).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, is_staff=True):
        # project_id should be in session
        session = client.session
        session["project_id"] = project.id
        session.save()
        data = {
            "intent": "read this",
            "content": "some nice content",
            "notify_email": True,
        }
        response = client.post(url, data=data)

    # a new Recommmendation is created
    task = models.Task.objects.all()[0]
    assert task.project == project
    assert task.resource == resource
    assert task.content == data["content"]
    assert task.intent == data["intent"]

    # notification is found
    assert len(get_messages(response.wsgi_request)) > 0

    # user is redirected to project
    newurl = reverse("projects-project-detail", args=[project.id])
    assertRedirects(response, newurl)
    # sessions is cleaned up
    assert "project_id" not in client.session


########################################################################
# template tags and filters
########################################################################


@pytest.mark.django_db
def test_current_project_tag():
    project = Recipe(models.Project).make()
    session = {"project_id": project.id}
    assert projects_extra.current_project(session) == project


# eof
