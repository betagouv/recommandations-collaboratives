# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""


import pytest
from actstream.models import action_object_stream
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains
from urbanvitaliz.utils import login

from .. import models

########################################################################
# notes
########################################################################


# Public conversation
@pytest.mark.django_db
def test_create_conversation_message_not_available_for_non_logged_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-conversation-create-message", args=[project.id])
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_conversation_message_not_available_for_outsiders(client):
    with login(client):
        project = Recipe(models.Project).make()
        url = reverse("projects-conversation-create-message", args=[project.id])
        response = client.post(
            url,
            data={"content": "this is some content"},
        )
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_conversation_message_available_for_project_collaborators(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email, status="READY").make()
        url = reverse("projects-conversation-create-message", args=[project.id])
        response = client.post(
            url,
            data={"content": "this is some content"},
        )
    note = models.Note.objects.all()[0]
    assert note.project == project
    assert response.status_code == 302


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
def test_create_note_available_for_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-create-note", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-add-note"')


@pytest.mark.django_db
def test_create_note_available_for_project_collaborators(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        url = reverse("projects-create-note", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-add-note"')


@pytest.mark.django_db
def test_create_new_note_for_project_and_redirect(client):
    project = Recipe(models.Project).make()
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content"},
        )
    note = models.Note.fetch()[0]
    assert note.project == project
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_public_note_for_project_collaborator_and_redirect(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content"},
        )
    note = models.Note.fetch()[0]
    assert note.project == project
    assert note.public is True
    assert note.created_by is not None
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_private_note_not_available_for_project_collaborator(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content", "public": False},
        )
    note = models.Note.fetch()[0]
    assert note.project == project
    assert note.public is True
    assert response.status_code == 302


@pytest.mark.django_db
def test_private_note_hidden_from_project_members(client):
    user_email = "not@admin.here"
    Recipe(models.Project, status="READY", emails=[user_email]).make()

    note = Recipe(models.Note, content="short note", public=False).make()

    with login(client, username="project_owner", email=user_email, is_staff=False):
        response = client.get(note.get_absolute_url())

    assert response.status_code == 403


@pytest.mark.django_db
def test_public_note_available_to_readers(client):
    user_email = "not@admin.here"
    note_content = "this is a public note"
    project = Recipe(models.Project, emails=[user_email], status="READY").make()
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        response = client.post(
            reverse("projects-conversation-create-message", args=[project.id]),
            data={"content": note_content, "public": True},
        )

    note = models.Note.objects.first()
    with login(client, username="project_owner", email=user_email, is_staff=False):
        response = client.get(note.get_absolute_url())

    assertContains(response, note_content)


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
def test_update_note_available_for_switchtender(client):
    note = Recipe(models.Note).make()
    url = reverse("projects-update-note", args=[note.id])
    with login(client, groups=["switchtender"]) as user:
        note.project.switchtenders.add(user)
        response = client.get(url)
    assert response.status_code == 200

    assertContains(response, 'form id="form-projects-update-note"')


@pytest.mark.django_db
def test_update_public_note_for_project_collaborator_and_redirect(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        note = Recipe(models.Note, project=project, public=True).make()
        response = client.post(
            reverse("projects-update-note", args=[note.id]),
            data={"content": "this is some content"},
        )
    note = models.Note.fetch()[0]
    assert note.project == project
    assert note.public is True
    assert response.status_code == 302


@pytest.mark.django_db
def test_update_private_note_for_project_collaborator(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        note = Recipe(models.Note, project=project, public=False).make()
        url = reverse("projects-update-note", args=[note.id])
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_update_note_for_project_and_redirect(client):
    note = Recipe(models.Note).make()
    updated_on_before = note.updated_on
    url = reverse("projects-update-note", args=[note.id])
    data = {"content": "this is some content"}

    with login(client, groups=["switchtender"]) as user:
        note.project.switchtenders.add(user)
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

    with login(client, groups=["switchtender"]):
        response = client.post(url)

    assert models.Note.objects.count() == 0

    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_note_removes_activity(client):
    project = Recipe(models.Project).make()

    with login(client, username="addman", groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "content", "public": True},
        )

    note = models.Note.objects.first()
    assert note

    assert action_object_stream(note).count()

    with login(client, username="removeman", groups=["switchtender"]):
        client.post(reverse("projects-delete-note", args=[note.id]))

    assert action_object_stream(note).count() == 0
