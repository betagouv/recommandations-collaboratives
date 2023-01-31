# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2023-01-31 14:24:56 CEST
"""


import pytest
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker
from django.shortcuts import reverse
from urbanvitaliz.utils import login
from django.test import RequestFactory
from notifications.signals import notify

from .. import models
from .. import context_processors


@pytest.mark.django_db
def test_active_project_processor(request, client):
    current_site = get_current_site(request)

    user = baker.make(auth_models.User, is_staff=False)
    project = baker.make(
        models.Project, members=[user], sites=[current_site], status="READY"
    )

    objects = (
        baker.make(models.Document, project=project, the_link="http://nowhe.re"),
        baker.make(models.Note, project=project, public=True),
        baker.make(models.Note, project=project, public=False),
        baker.make(models.Task, project=project, public=False),
    )

    for obj in objects:
        notify.send(
            sender=user, recipient=user, verb="verb", action_object=obj, target=project
        )

    with login(client, user=user):
        response = client.get(
            reverse("projects-project-detail-overview", args=[project.pk])
        )

    assert response.context["active_project"] == project

    notifs = (
        "active_project_action_notifications_count",
        "active_project_conversation_notifications_count",
        "active_project_document_notifications_count",
        "active_project_private_conversation_notifications_count",
    )

    for notif in notifs:
        assert response.context[notif] == 1, f"{notif} expected 1"


# eof
