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


@pytest.fixture()
def msg_and_sender(project_ready):
    user = baker.make(auth_models.User)
    assign_perm("projects.use_public_notes", user, project_ready)
    message = baker.make(Message, project=project_ready, posted_by=user)
    message.save()
    return message, user


@pytest.fixture()
def sender(msg_and_sender):
    return msg_and_sender[1]


@pytest.fixture()
def message(msg_and_sender):
    return msg_and_sender[0]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "msg_reader,res_code",
    [
        ("project_editor", 200),
        ("project_reader", 200),
        ("random_user", 403),
    ],
)
def test_who_can_read_messages(
    msg_reader, res_code, project_ready, msg_and_sender, request, client
):
    user = request.getfixturevalue(msg_reader)
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
        ("sender", 200),
        ("project_editor", 403),
        ("project_reader", 403),
        ("random_user", 403),
    ],
)
@pytest.mark.django_db
def test_who_can_edit_messages(
    msg_reader, res_code, project_ready, message, request, client
):
    user = request.getfixturevalue(msg_reader)
    url = reverse(
        "projects-conversations-messages-detail", args=[project_ready.pk, message.pk]
    )
    client.force_login(user)
    data = {"nodes": []}
    response = client.patch(url, json.dumps(data), content_type="application/json")
    assert response.status_code == res_code


@pytest.mark.parametrize(
    "msg_reader,res_code",
    [
        ("sender", 204),
        ("project_editor", 403),
        ("project_reader", 403),
        ("random_user", 403),
    ],
)
@pytest.mark.django_db
def test_who_can_delete_messages(
    msg_reader, res_code, project_ready, message, request, client
):
    user = request.getfixturevalue(msg_reader)
    url = reverse(
        "projects-conversations-messages-detail", args=[project_ready.pk, message.pk]
    )
    client.force_login(user)
    response = client.delete(url)
    assert response.status_code == res_code


@pytest.mark.parametrize(
    "msg_reader,res_code",
    [
        ("project_editor", 200),
        ("project_reader", 200),
        ("random_user", 403),
    ],
)
@pytest.mark.django_db
def test_who_can_see_activity(msg_reader, res_code, project_ready, request, client):
    user = request.getfixturevalue(msg_reader)
    url = reverse("projects-conversations-activities-list", args=[project_ready.pk])
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == res_code
    pass


@pytest.mark.parametrize(
    "msg_reader,res_code",
    [
        ("project_editor", 200),
        ("project_reader", 200),
        ("random_user", 403),
    ],
)
@pytest.mark.django_db
def test_who_can_see_participants(
    msg_reader, project_editor, project_reader, res_code, project_ready, request, client
):
    user = request.getfixturevalue(msg_reader)
    baker.make(auth_models.User)
    project_ready.members.set(
        (
            project_editor,
            project_reader,
            baker.make(auth_models.User),
            baker.make(auth_models.User),
        )
    )
    url = reverse("projects-conversations-participants-list", args=[project_ready.pk])
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == res_code


@pytest.mark.django_db
def test_delete_message(message, sender, project_ready, client):
    url = reverse(
        "projects-conversations-messages-detail", args=[project_ready.pk, message.pk]
    )
    client.force_login(sender)
    client.delete(url)

    msg = Message.objects.filter(pk=message.pk).first()
    msg_not_deleted = Message.not_deleted.filter(pk=message.pk).first()
    assert msg.deleted is not None
    assert msg_not_deleted is None


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

    post_public_message_with_recommendation(task, "message")

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
