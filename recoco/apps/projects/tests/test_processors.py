# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2023-01-31 14:24:56 CEST
"""

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import reverse
from model_bakery import baker
from notifications.signals import notify

from recoco.apps.conversations import models as conversation_models
from recoco.apps.home import models as home_models
from recoco.apps.tasks import models as task_models
from recoco.utils import login

from .. import models, utils
from ..context_processors import unread_notifications_processor


@pytest.mark.django_db
def test_active_project_processor(request, client):
    current_site = get_current_site(request)

    baker.make(home_models.SiteConfiguration, site=current_site)

    project = baker.make(models.Project)
    project.project_sites.create(site=current_site, status="READY", is_origin=True)

    objects = (
        baker.make(models.Document, project=project, the_link="http://nowhe.re"),
        baker.make(conversation_models.Message, project=project),
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

        assert "unread_notifications_count" in response.context


@pytest.mark.django_db
def test_unread_notifications_processor_includes_private_notifications(
    rf, project_ready, current_site
):
    baker.make(home_models.SiteConfiguration, site=current_site)

    user = baker.make(auth_models.User)
    utils.assign_collaborator(user, project_ready)

    notify.send(
        sender=user,
        recipient=user,
        verb="a public notification",
        action_object=project_ready,
        target=project_ready,
        public=True,
    )
    notify.send(
        sender=user,
        recipient=user,
        verb="a private notification",
        action_object=project_ready,
        target=project_ready,
        public=False,
    )

    request = rf.get("/")
    request.user = user
    request.site = current_site

    context = unread_notifications_processor(request)

    assert context["unread_notifications_count"] == 2


# eof
