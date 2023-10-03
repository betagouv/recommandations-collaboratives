# encoding: utf-8

"""
Tests for project application / administration

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-12-26 11:54:56 CEST
"""


import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from urbanvitaliz.apps.tasks import models as tasks_models
from urbanvitaliz.apps.invites.api import invite_collaborator_on_project
from urbanvitaliz.apps.projects.utils import assign_advisor, assign_collaborator
from urbanvitaliz.utils import assign_site_staff, login

from .. import models


#################################################################
# Project (in)activation
#################################################################

# -- Inactivate project


@pytest.mark.django_db
def test_owner_can_set_project_inactive_without_reason(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    url = reverse(
        "projects-project-set-inactive",
        args=[project.id],
    )

    with login(client) as user:
        assign_collaborator(user, project, is_owner=True)
        response = client.post(url)

    assert response.status_code == 202

    project = models.Project.on_site.get(id=project.id)

    assert project.inactive_since is not None
    assert project.inactive_reason == ""


@pytest.mark.django_db
def test_owner_can_set_project_inactive_with_reason(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    url = reverse(
        "projects-project-set-inactive",
        args=[project.id],
    )

    with login(client) as user:
        assign_collaborator(user, project, is_owner=True)
        response = client.post(url, data={"inactive_reason": "because"})

    assert response.status_code == 202

    project = models.Project.on_site.get(id=project.id)

    assert project.inactive_since is not None
    assert project.inactive_reason == "because"


@pytest.mark.django_db
def test_site_staff_can_set_project_inactive(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    url = reverse(
        "projects-project-set-inactive",
        args=[project.id],
    )

    with login(client) as user:
        assign_site_staff(site, user)
        response = client.post(url)

    assert response.status_code == 202

    project = models.Project.on_site.get(id=project.id)

    assert project.inactive_since is not None
    assert project.inactive_reason == ""


@pytest.mark.django_db
def test_regular_collaborator_cannot_set_project_inactive(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    url = reverse(
        "projects-project-set-inactive",
        args=[project.id],
    )

    with login(client) as user:
        assign_collaborator(user, project, is_owner=False)

        response = client.post(url)

    assert response.status_code == 403

    project = models.Project.on_site.get(id=project.id)
    assert project.inactive_since is None


# -- Activate project


@pytest.mark.django_db
def test_owner_can_set_project_active(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        inactive_since=timezone.now(),
    )

    url = reverse(
        "projects-project-set-active",
        args=[project.id],
    )

    with login(client) as user:
        assign_collaborator(user, project, is_owner=True)
        response = client.post(url)

    assert response.status_code == 202

    project = models.Project.on_site.get(id=project.id)

    assert project.inactive_since is None


@pytest.mark.django_db
def test_site_staff_can_set_project_active(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        inactive_since=timezone.now(),
    )

    url = reverse(
        "projects-project-set-active",
        args=[project.id],
    )

    with login(client) as user:
        assign_site_staff(site, user)
        response = client.post(url)

    assert response.status_code == 202

    project = models.Project.on_site.get(id=project.id)

    assert project.inactive_since is None


@pytest.mark.django_db
def test_regular_collaborator_cannot_set_project_active(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        inactive_since=timezone.now(),
    )

    url = reverse(
        "projects-project-set-active",
        args=[project.id],
    )

    with login(client) as user:
        assign_collaborator(user, project, is_owner=False)

        response = client.post(url)

    assert response.status_code == 403

    updated = models.Project.on_site.get(id=project.id)
    assert updated.inactive_since == project.inactive_since


# -- Notification dispatching when project is set inactive


@pytest.mark.django_db
def test_notifications_are_not_dispatched_to_collaborators_if_project_is_inactive(
    request, client, subtests
):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        inactive_since=timezone.now(),
    )
    task = baker.make(
        tasks_models.Task, project=project, site=get_current_site(request)
    )

    owner = baker.make(auth_models.User, email="owner@notif.com")
    assign_collaborator(owner, project, is_owner=True)

    collaborator = baker.make(auth_models.User, email="collab@notif.com")
    assign_collaborator(collaborator, project)

    invited_collab = baker.make(auth_models.User, email="invited_collab@notif.com")

    advisor = baker.make(auth_models.User, email="advisor@notif.com")
    assign_advisor(advisor, project, site)

    superuser = baker.make(auth_models.User, is_superuser=True)

    invite = invite_collaborator_on_project(
        site,
        project,
        "COLLABORATOR",
        invited_collab.email,
        "hey",
        collaborator,
    )

    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")

    triggers = [
        {
            "url-name": "projects-project-switchtender-join",
            "url-args": {"project_id": project.pk},
            "user": superuser,
            "post-data": {},
        },  # advisor joined ✓
        {
            "url-name": "projects-project-observer-join",
            "url-args": {"project_id": project.pk},
            "user": superuser,
            "post-data": {},
        },  # observer joined ✓
        {
            "url-name": "invites-invite-accept",
            "url-args": {"invite_id": invite.pk},
            "user": invited_collab,
            "post-data": {},
        },  # project member joined ✓
        {
            "url-name": "projects-conversation-create-message",
            "url-args": {"project_id": project.pk},
            "user": superuser,
            "post-data": {"content": "this is some content"},
        },  # public conversation posted ✓
        {
            "url-name": "projects-documents-upload-document",
            "url-args": {"project_id": project.pk},
            "user": superuser,
            "post-data": {"description": "this is some content", "the_file": png},
        },  # document uploaded ✓
        {
            "url-name": "projects-project-create-task",
            "url-args": {"project_id": project.pk},
            "user": superuser,
            "post-data": {
                "push_type": "noresource",
                "intent": "yeah",
                "content": "this is some content",
                "public": True,
            },
        },  # reco published ✓
        {
            "url-name": "projects-followup-task",
            "url-args": {"task_id": task.pk},
            "user": superuser,
            "post-data": {"comment": "hey"},
        },  # reco commented ✓
    ]

    for trigger in triggers:
        with subtests.test(trigger["url-name"]):
            url = reverse(trigger["url-name"], kwargs=trigger["url-args"])
            with login(client, user=trigger["user"]):
                response = client.post(url, data=trigger["post-data"])
                assert response.status_code == 302, trigger["url-name"]

            assert not collaborator.notifications.exists()
            assert advisor.notifications.exists()


# -- Implicit reactivation
@pytest.mark.django_db
def test_project_is_reactivated_on_conversation_message(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        inactive_since=timezone.now(),
    )

    url = reverse(
        "projects-conversation-create-message", kwargs={"project_id": project.pk}
    )

    with login(client) as owner:
        assign_collaborator(owner, project, is_owner=True)
        response = client.post(url, data={"content": "this is some content"})

    assert response.status_code == 302

    project.refresh_from_db()

    assert project.inactive_since is None


@pytest.mark.django_db
def test_project_is_reactivated_on_document_upload(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        inactive_since=timezone.now(),
    )

    url = reverse(
        "projects-documents-upload-document", kwargs={"project_id": project.pk}
    )

    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")

    with login(client) as owner:
        assign_collaborator(owner, project, is_owner=True)
        response = client.post(
            url, data={"description": "this is some content", "the_file": png}
        )

    assert response.status_code == 302

    project.refresh_from_db()

    assert project.inactive_since is None


@pytest.mark.django_db
def test_project_is_reactivated_on_recommendation_comment(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        inactive_since=timezone.now(),
    )

    task = baker.make(
        tasks_models.Task, project=project, site=get_current_site(request)
    )

    url = reverse("projects-followup-task", kwargs={"task_id": task.pk})

    with login(client) as owner:
        assign_collaborator(owner, project, is_owner=True)
        response = client.post(url, data={"comment": "hey"})

    assert response.status_code == 302

    project.refresh_from_db()

    assert project.inactive_since is None


@pytest.mark.django_db
def test_project_is_reactivated_on_survey_edition(request, client):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        inactive_since=timezone.now(),
    )

    task = baker.make(
        tasks_models.Task, project=project, site=get_current_site(request)
    )

    url = reverse("projects-followup-task", kwargs={"task_id": task.pk})

    with login(client) as owner:
        assign_collaborator(owner, project, is_owner=True)
        response = client.post(url, data={"comment": "hey"})

    assert response.status_code == 302

    project.refresh_from_db()

    assert project.inactive_since is None


# ...,  # survey edited?


# eof
