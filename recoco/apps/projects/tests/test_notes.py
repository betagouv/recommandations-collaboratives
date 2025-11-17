# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

import pytest
from actstream.models import action_object_stream
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains

from recoco import verbs
from recoco.utils import login

from .. import models
from ..utils import assign_advisor, assign_collaborator

########################################################################
# notes
########################################################################

# create


@pytest.mark.django_db
def test_create_note_not_available_for_non_staff_users(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-create-note", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_note_available_for_advisor(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-create-note", args=[project.id])

    with login(client) as user:
        assign_advisor(user, project)
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-add-note"')


@pytest.mark.django_db
def test_create_private_note_not_available_for_project_collaborator(
    request, client, project
):
    with login(client) as user:
        assign_collaborator(user, project)

        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content"},
        )

    assert response.status_code == 403


@pytest.mark.django_db
def test_switchtender_creates_new_private_note_for_project_and_redirect(
    request, client, project_ready
):
    with login(client) as user:
        assign_advisor(user, project_ready)

        response = client.post(
            reverse("projects-create-note", args=[project_ready.id]),
            data={"content": "this is some content"},
        )
    assert response.status_code == 302

    note = models.Note.on_site.all()[0]
    assert note.project == project_ready
    assert note.public is False

    # stream and notifications
    actions = action_object_stream(note)
    assert actions.count() == 1
    assert actions[0].verb == verbs.Conversation.PRIVATE_MESSAGE


@pytest.mark.django_db
def test_private_note_hidden_from_project_members(request, client, project):
    membership = baker.make(models.ProjectMember, member__is_staff=False)
    project.projectmember_set.add(membership)

    note = baker.make(models.Note, project=project, content="short note", public=False)

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.get(note.get_absolute_url())

    assert response.status_code == 403


#
# update


@pytest.mark.django_db
def test_update_note_not_available_for_non_staff_users(request, client):
    note = Recipe(models.Note, site=get_current_site(request)).make()
    url = reverse("projects-update-note", args=[note.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_advisor_can_update_own_note(request, client):
    site = get_current_site(request)

    with login(client) as user:
        note = Recipe(models.Note, site=site, created_by=user).make()
        url = reverse("projects-update-note", args=[note.id])

        assign_advisor(user, note.project, site)

        response = client.get(url)
    assert response.status_code == 200

    assertContains(response, 'form id="form-projects-update-note"')


@pytest.mark.django_db
def test_advisor_cant_update_other_advisor_note(request, client):
    current_site = get_current_site(request)
    note = Recipe(models.Note, site=current_site).make()
    url = reverse("projects-update-note", args=[note.id])

    with login(client, groups=["example_com_advisor"]) as user:
        assign_advisor(user, note.project, current_site)
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_collaborator_cant_update_private_note(request, client, project):
    note = Recipe(
        models.Note, public=False, project=project, site=get_current_site(request)
    ).make()
    with login(client) as user:
        assign_collaborator(user, note.project)
        url = reverse("projects-update-note", args=[note.id])
        response = client.get(url)

    assert response.status_code == 403


########################################################################
# DELETION
########################################################################


@pytest.mark.django_db
def test_advisor_can_delete_private_note_and_redirect(request, client, project):
    current_site = get_current_site(request)

    note = Recipe(models.Note, project=project, site=current_site, public=False).make()
    url = reverse("projects-delete-note", args=[note.id])

    with login(client) as user:
        assign_advisor(user, project)
        response = client.post(url)

    assert models.Note.on_site.count() == 0

    assert response.status_code == 302


@pytest.mark.django_db
def test_collaborator_cant_delete_other_people_note(request, client, project):
    current_site = get_current_site(request)

    with login(client) as user:
        note = Recipe(
            models.Note,
            project=project,
            site=current_site,
            public=False,
        ).make()

        url = reverse("projects-delete-note", args=[note.id])

        assign_collaborator(user, project)
        response = client.post(url)

    assert models.Note.on_site.count() == 1

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_note_removes_activity(request, client, project):
    with login(client, username="addman") as user:
        assign_advisor(user, project)

        client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "content", "public": True},
        )

    note = models.Note.on_site.first()
    assert note

    assert action_object_stream(note).count()

    with login(client, username="removeman") as user:
        assign_advisor(user, project)
        client.post(reverse("projects-delete-note", args=[note.id]))

    assert action_object_stream(note).count() == 0


# eof
