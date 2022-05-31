# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-05-31 10:11:56 CEST
"""


import pytest
from actstream.models import action_object_stream
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains
from urbanvitaliz.utils import login

from .. import models


@pytest.mark.django_db
def test_upload_document_not_available_for_non_logged_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-conversation-upload-file", args=[project.id])
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_upload_document_available_for_project_collaborators(client):
    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")
    data = {"description": "this is some content", "the_file": png}

    with login(client) as user:
        project = Recipe(models.Project, email=user.email, status="READY").make()
        url = reverse("projects-conversation-upload-file", args=[project.id])
        response = client.post(url, data=data)

    assert response.status_code == 302

    document = models.Document.objects.all()[0]
    assert document.project == project
    assert document.description == data["description"]
    assert document.uploaded_by == user
    assert document.the_file is not None
