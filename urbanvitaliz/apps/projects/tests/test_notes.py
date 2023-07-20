# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""


import notifications
import pytest
from actstream.models import action_object_stream
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from notifications import notify
from pytest_django.asserts import assertContains

from urbanvitaliz import verbs
from urbanvitaliz.utils import login

from .. import models
from ..utils import assign_advisor, assign_collaborator

########################################################################
# notes
########################################################################


# Public conversation
@pytest.mark.django_db
def test_create_conversation_message_not_available_for_non_logged_users(
    request, client
):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-conversation-create-message", args=[project.id])
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_conversation_message_not_available_for_outsiders(request, client):
    with login(client):
        project = Recipe(models.Project, sites=[get_current_site(request)]).make()
        url = reverse("projects-conversation-create-message", args=[project.id])
        response = client.post(
            url,
            data={"content": "this is some content"},
        )
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_conversation_message_available_for_project_collaborators(
    request, client
):
    user = baker.make(auth_models.User)
    project = Recipe(
        models.Project, status="READY", sites=[get_current_site(request)]
    ).make()

    assign_collaborator(user, project)

    with login(client, user=user):
        url = reverse("projects-conversation-create-message", args=[project.id])
        response = client.post(
            url,
            data={"content": "this is some content"},
        )
    note = models.Note.on_site.all()[0]
    assert note.project == project
    assert response.status_code == 302


#
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
def test_create_private_note_not_available_for_project_collaborator(request, client):
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
    ).make()

    with login(client) as user:
        assign_collaborator(user, project)

        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content"},
        )

    assert response.status_code == 403


@pytest.mark.django_db
def test_switchtender_creates_new_private_note_for_project_and_redirect(
    request, client
):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()

    with login(client) as user:
        assign_advisor(user, project)

        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content"},
        )
    assert response.status_code == 302

    note = models.Note.on_site.all()[0]
    assert note.project == project
    assert note.public is False

    # stream and notifications
    actions = action_object_stream(note)
    assert actions.count() == 1
    assert actions[0].verb == verbs.Conversation.PRIVATE_MESSAGE


@pytest.mark.django_db
def test_create_public_note_for_project_collaborator_and_redirect(request, client):
    membership = baker.make(models.ProjectMember, member__is_staff=False)

    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
        projectmember_set=[membership],
    ).make()

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.post(
            reverse("projects-conversation-create-message", args=[project.id]),
            data={"content": "this is some content"},
        )
    assert response.status_code == 302

    note = models.Note.on_site.all()[0]
    assert note.project == project
    assert note.public is True

    # stream and notifications
    actions = action_object_stream(note)
    assert actions.count() == 1
    assert actions[0].verb == verbs.Conversation.PUBLIC_MESSAGE

    assert notifications.models.Notification.objects.count() == 1


@pytest.mark.django_db
def test_private_note_hidden_from_project_members(request, client):
    membership = baker.make(models.ProjectMember, member__is_staff=False)
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
        projectmember_set=[membership],
    )

    note = baker.make(models.Note, project=project, content="short note", public=False)

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.get(note.get_absolute_url())

    assert response.status_code == 403


@pytest.mark.django_db
def test_advisor_public_note_available_to_collaborators(request, client):
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
    ).make()
    note_content = "this is a public note"

    with login(client, username="advisor") as user:
        assign_advisor(user, project)

        response = client.post(
            reverse("projects-conversation-create-message", args=[project.id]),
            data={"content": note_content, "public": True},
        )

    note = models.Note.objects.first()
    assert note.content == note_content

    with login(client, username="collaborator") as user:
        assign_collaborator(user, project)
        response = client.get(note.get_absolute_url())

    assertContains(response, note_content)


@pytest.mark.django_db
def test_create_conversation_message_with_attachment_for_project_collaborator(
    request, client
):
    project = Recipe(
        models.Project, sites=[get_current_site(request)], status="READY"
    ).make()

    with login(client, username="collaborator") as user:
        assign_collaborator(user, project)
        png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")
        response = client.post(
            reverse("projects-conversation-create-message", args=[project.id]),
            data={
                "content": "this is some content",
                "the_file": png,
            },
        )

    assert response.status_code == 302

    note = models.Note.on_site.first()
    assert note
    document = models.Document.on_site.first()
    assert document
    assert document.the_file != ""
    assert document.attached_object == note


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
def test_collaborator_can_update_own_public_note(request, client):
    current_site = get_current_site(request)
    project = Recipe(
        models.Project,
        sites=[current_site],
    ).make()
    with login(client) as user:
        assign_collaborator(user, project)

        note = Recipe(
            models.Note,
            created_by=user,
            project=project,
            public=True,
            site=current_site,
        ).make()

        response = client.post(
            reverse("projects-update-note", args=[note.id]),
            data={"content": "this is some content"},
        )

    note = models.Note.on_site.all()[0]
    assert note.project == project
    assert note.public is True
    assert response.status_code == 302


@pytest.mark.django_db
def test_collaborator_cannot_update_others_public_note(request, client):
    current_site = get_current_site(request)
    project = Recipe(
        models.Project,
        sites=[current_site],
    ).make()

    with login(client) as user:
        assign_collaborator(user, project)
        note = Recipe(
            models.Note, project=project, public=False, site=current_site
        ).make()

        response = client.post(
            reverse("projects-update-note", args=[note.id]),
            data={"content": "this is some content"},
        )

    assert response.status_code == 403


@pytest.mark.django_db
def test_collaborator_cant_update_private_note(request, client):
    note = Recipe(models.Note, public=False, site=get_current_site(request)).make()
    with login(client) as user:
        assign_collaborator(user, note.project)
        url = reverse("projects-update-note", args=[note.id])
        response = client.get(url)

    assert response.status_code == 403


########################################################################
# DELETION
########################################################################


@pytest.mark.django_db
def test_advisor_can_delete_private_note_and_redirect(request, client):
    current_site = get_current_site(request)
    project = Recipe(models.Project, sites=[current_site]).make()
    note = Recipe(models.Note, project=project, site=current_site, public=False).make()
    url = reverse("projects-delete-note", args=[note.id])

    with login(client) as user:
        assign_advisor(user, project)
        response = client.post(url)

    assert models.Note.on_site.count() == 0

    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_my_public_note_for_collaborator_and_redirect(request, client):
    current_site = get_current_site(request)
    project = Recipe(models.Project, sites=[current_site]).make()

    with login(client) as user:
        note = Recipe(
            models.Note,
            project=project,
            site=current_site,
            public=True,
            created_by=user,
        ).make()

        notify.send(
            sender=user,
            recipient=user,
            verb="sent note",
            action_object=note,
            target=project,
        )

        url = reverse("projects-delete-note", args=[note.id])

        assign_collaborator(user, project)
        response = client.post(url)

    # Note is deleted
    assert models.Note.on_site.count() == 0

    # associated notifications also
    assert notifications.models.Notification.objects.count() == 0

    assert response.status_code == 302


@pytest.mark.django_db
def test_collaborator_cant_delete_other_people_public_note(request, client):
    current_site = get_current_site(request)
    project = Recipe(models.Project, sites=[current_site]).make()

    with login(client) as user:
        note = Recipe(
            models.Note,
            project=project,
            site=current_site,
            public=True,
        ).make()

        url = reverse("projects-delete-note", args=[note.id])

        assign_collaborator(user, project)
        response = client.post(url)

    assert models.Note.on_site.count() == 1

    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_note_removes_activity(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()

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
