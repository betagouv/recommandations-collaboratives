# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2023-01-31 14:24:56 CEST
"""


import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import reverse
from model_bakery import baker
from notifications.signals import notify

from recoco.apps.home import models as home_models
from recoco.apps.tasks import models as task_models
from recoco.utils import login

from .. import models, utils


@pytest.mark.django_db
def test_active_project_processor(request, client):
    current_site = get_current_site(request)

    baker.make(home_models.SiteConfiguration, site=current_site)

    project = baker.make(models.Project, sites=[current_site], status="READY")

    objects = (
        baker.make(models.Document, project=project, the_link="http://nowhe.re"),
        baker.make(models.Note, project=project, public=True),
        baker.make(models.Note, project=project, public=False),
        baker.make(task_models.Task, project=project, public=False),
        # NOTE should we also add a Task w/ public=True ?
    )

    with login(client) as user:
        utils.assign_collaborator(user, project)
        for obj in objects:
            notify.send(
                sender=user,
                recipient=user,
                verb="a fake verb",
                action_object=obj,
                target=project,
            )

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
