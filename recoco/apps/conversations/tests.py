import json

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker

from recoco.apps.tasks import models as tasks_models
from recoco.apps.tasks import signals as tasks_signals

from .models import Message
from .utils import post_public_message_with_recommendation


#####--- Views ---#####
@pytest.fixture()
def project_reader(project_ready):
    project_reader = baker.make(auth_models.User)
    assign_perm("projects.view_public_notes", project_reader, project_ready)
    return project_reader


@pytest.fixture()
def project_editor(project_ready):
    project_editor = baker.make(auth_models.User)
    assign_perm("projects.view_public_notes", project_editor, project_ready)
    assign_perm("projects.use_public_notes", project_editor, project_ready)
    return project_editor


@pytest.fixture()
def random_user():
    user = baker.make(auth_models.User)
    return user


@pytest.mark.django_db
@pytest.mark.parametrize(
    "msg_reader,res_code",
    [
        ("project_editor", 200),
        ("project_reader", 200),
        ("random_user", 403),
    ],
)
def test_who_can_read_messages(msg_reader, res_code, project_ready, request, client):
    user = request.getfixturevalue(msg_reader)
    message = baker.make(Message, project=project_ready)
    message.save()
    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == res_code


@pytest.mark.parametrize(
    "msg_reader,res_code",
    [
        ("project_editor", 201),
        ("project_reader", 403),
        ("random_user", 403),
    ],
)
@pytest.mark.django_db
def test_who_can_send_messages(msg_reader, res_code, project_ready, request, client):
    user = request.getfixturevalue(msg_reader)
    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])
    client.force_login(user)
    data = {
        "nodes": [
            {"position": 1, "type": "MarkdownNode", "text": "One two this is a test"}
        ],
        "posted_by": user.id,
    }
    # when given directly, nested dict is not parsed correctly
    response = client.post(url, json.dumps(data), content_type="application/json")
    assert response.status_code == res_code


@pytest.mark.parametrize(
    "msg_reader,res_code",
    [
        ("project_editor", 403),
        ("project_reader", 403),
        ("random_user", 403),
    ],
)
@pytest.mark.django_db
def test_who_can_edit_messages(msg_reader, res_code, project_ready, request, client):
    user = request.getfixturevalue(msg_reader)
    message = baker.make(Message, project=project_ready)
    message.save()
    url = reverse(
        "projects-conversations-messages-detail", args=[project_ready.pk, message.pk]
    )
    client.force_login(user)
    response = client.patch(url, data={"nodes": []})
    assert response.status_code == res_code


#####--- Utils ---#####
@pytest.mark.django_db
def test_post_message_with_recommendation(project_ready, request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    task = baker.make(
        tasks_models.Task,
        public=True,
        project=project_ready,
        site=current_site,
        created_by=user,
    )

    assert Message.objects.count() == 0

    post_public_message_with_recommendation(project_ready, task)

    assert Message.objects.count() == 1


#####--- Signals ---#####
@pytest.mark.django_db
def test_message_is_posted_upon_reco_creation(project_ready, request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    assert Message.objects.count() == 0

    tasks_signals.action_created.send(
        sender=test_message_is_posted_upon_reco_creation,
        task=tasks_models.Task.objects.create(
            public=True,
            project=project_ready,
            site=current_site,
            created_by=user,
        ),
        project=project_ready,
        user=user,
    )

    assert Message.objects.count() == 1
