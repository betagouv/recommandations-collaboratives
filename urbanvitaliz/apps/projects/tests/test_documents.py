# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-05-31 10:11:56 CEST
"""


import pytest
from actstream.models import action_object_stream
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from urbanvitaliz.utils import login

from .. import models


@pytest.mark.django_db
def test_project_documents_not_available_for_non_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-documents", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_overview_available_for_owner(request, client):
    current_site = get_current_site(request)

    # project email is same as test user to be logged in
    membership = baker.make(models.ProjectMember, member__is_staff=False, is_owner=True)
    project = Recipe(
        models.Project, sites=[current_site], projectmember_set=[membership]
    ).make()

    with login(client, user=membership.member, is_staff=False):
        url = reverse("projects-project-detail-documents", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_upload_document_not_available_for_non_logged_users(client, request):
    project = baker.make(models.Project, sites=[get_current_site(request)])
    url = reverse("projects-documents-upload-document", args=[project.id])
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_upload_file_available_for_project_collaborators(client, request):
    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")
    data = {"description": "this is some content", "the_file": png}

    membership = baker.make(models.ProjectMember, is_owner=True, member__is_staff=False)
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    with login(client, user=membership.member):
        url = reverse("projects-documents-upload-document", args=[project.id])
        response = client.post(url, data=data)

    assert response.status_code == 302

    document = models.Document.objects.all()[0]
    assert document.project == project
    assert document.description == data["description"]
    assert document.uploaded_by == membership.member
    assert document.the_file is not None


from django.db import transaction


def test_upload_document_is_either_link_or_file(client, request):
    data = {"description": "this is some content"}

    membership = baker.make(models.ProjectMember, is_owner=True, member__is_staff=False)
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    with login(client, user=membership.member):
        url = reverse("projects-documents-upload-document", args=[project.id])
        with transaction.atomic():
            client.post(url, data=data)

    assert models.Document.objects.count() == 0


@pytest.mark.django_db
def test_upload_file_triggers_notifications(client, request):
    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")
    data = {"description": "this is some content", "the_file": png}

    membership = baker.make(models.ProjectMember, is_owner=True, member__is_staff=False)
    other_membership = baker.make(
        models.ProjectMember,
        is_owner=False,
        member__is_staff=False,
    )
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership, other_membership],
        status="READY",
    )

    with login(client, user=membership.member):
        url = reverse("projects-documents-upload-document", args=[project.id])
        response = client.post(url, data=data)

    assert response.status_code == 302

    document = models.Document.objects.all()[0]

    assert action_object_stream(document).count() == 1
    assert membership.member.notifications.count() == 0
    assert other_membership.member.notifications.count() == 1


@pytest.mark.django_db
def test_delete_document_not_available_for_non_logged_users(client, request):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-documents-delete-document", args=[project.id, 1])
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_document_available_for_owner(client, request):
    membership = baker.make(models.ProjectMember, is_owner=True, member__is_staff=False)
    project = baker.make(
        models.Project,
        projectmember_set=[membership],
        sites=[get_current_site(request)],
        status="READY",
    )
    document = baker.make(
        models.Document,
        uploaded_by=membership.member,
        project=project,
        the_link="http://yo",
        site=get_current_site(request),
    )

    with login(client, user=membership.member):
        url = reverse(
            "projects-documents-delete-document", args=[project.id, document.id]
        )
        response = client.post(url)

    assert response.status_code == 302
    document = models.Document.objects.count() == 0


@pytest.mark.django_db
def test_delete_document_not_available_for_others(client, request):
    membership = baker.make(models.ProjectMember, is_owner=True, member__is_staff=False)
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )
    document = baker.make(
        models.Document,
        project=project,
        the_link="http://yo",
        site=get_current_site(request),
        uploaded_by__username="other",
        description="Doc description",
    )

    with login(client, user=membership.member):
        url = reverse(
            "projects-documents-delete-document", args=[project.id, document.id]
        )
        response = client.post(url)

    assert response.status_code == 403
    document = models.Document.objects.count() == 1


@pytest.mark.django_db
def test_project_pin_document(request, client):
    current_site = get_current_site(request)

    # project email is same as test user to be logged in
    membership = baker.make(models.ProjectMember, member__is_staff=False, is_owner=True)
    project = Recipe(
        models.Project,
        status="READY",
        sites=[current_site],
        projectmember_set=[membership],
    ).make()

    document = baker.make(
        models.Document,
        uploaded_by=membership.member,
        project=project,
        the_link="http://yo",
        site=get_current_site(request),
    )

    with login(client, user=membership.member, is_staff=False):
        url = reverse("projects-documents-pin-unpin", args=[project.id, document.pk])
        response = client.post(url)

    assert response.status_code == 302

    document = models.Document.on_site.get(pk=document.pk)
    assert document.pinned is True


@pytest.mark.django_db
def test_project_unpin_document(request, client):
    current_site = get_current_site(request)

    # project email is same as test user to be logged in
    membership = baker.make(models.ProjectMember, member__is_staff=False, is_owner=True)
    project = Recipe(
        models.Project,
        status="READY",
        sites=[current_site],
        projectmember_set=[membership],
    ).make()

    document = baker.make(
        models.Document,
        uploaded_by=membership.member,
        project=project,
        the_link="http://yo",
        site=get_current_site(request),
        pinned=True,
    )

    with login(client, user=membership.member, is_staff=False):
        url = reverse("projects-documents-pin-unpin", args=[project.id, document.pk])
        response = client.post(url)

    assert response.status_code == 302

    document = models.Document.on_site.get(pk=document.pk)
    assert document.pinned is False
