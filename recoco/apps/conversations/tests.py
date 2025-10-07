import json

import pytest
from actstream.models import action_object_stream
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from notifications.models import Notification

from recoco import verbs
from recoco.apps.projects import models as projects_models
from recoco.apps.tasks import models as tasks_models
from recoco.apps.tasks import signals as tasks_signals
from recoco.utils import login

from . import signals
from .models import DocumentNode, Message
from .utils import (
    gather_annotations_for_message_notification,
    post_public_message_with_recommendation,
)


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
def ex_node_dict():
    return {"text": "toto", "type": "MarkdownNode", "position": 1}


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


#####--- Views ---#####
#####--- permissions ---#####


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
def test_who_can_send_messages(
    msg_reader, res_code, ex_node_dict, project_ready, request, client
):
    user = request.getfixturevalue(msg_reader)
    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])
    client.force_login(user)
    data = {"nodes": [ex_node_dict]}
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
    msg_reader, res_code, ex_node_dict, project_ready, message, request, client
):
    user = request.getfixturevalue(msg_reader)
    url = reverse(
        "projects-conversations-messages-detail", args=[project_ready.pk, message.pk]
    )
    client.force_login(user)
    data = {"nodes": [ex_node_dict]}
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


#####--- actions ---#####


@pytest.mark.django_db
def test_cannot_send_empty_message(sender, project_ready, request, client):
    user = sender
    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])
    client.force_login(user)
    data = {"nodes": []}
    # when given directly, nested dict is not parsed correctly
    response = client.post(url, json.dumps(data), content_type="application/json")
    assert response.status_code == 400
    assert str(response.data["nodes"][0]) == "A message must have at least one node."


@pytest.mark.django_db
def test_cannot_edit_empty_message(sender, project_ready, message, request, client):
    user = sender
    url = reverse(
        "projects-conversations-messages-detail", args=[project_ready.pk, message.pk]
    )
    client.force_login(user)
    data = {"nodes": []}
    response = client.patch(url, json.dumps(data), content_type="application/json")
    assert response.status_code == 400
    assert str(response.data["nodes"][0]) == "A message must have at least one node."


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


@pytest.mark.django_db
def test_post_message_with_document(project_ready, request, client, project_editor):
    current_site = get_current_site(request)

    doc = baker.make(
        projects_models.Document,
        site=current_site,
        project=project_ready,
        uploaded_by=project_editor,
        the_link="http://un.site.fr",
    )

    assert Message.objects.count() == 0

    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])
    client.force_login(project_editor)
    data = {
        "nodes": [{"position": 1, "type": "DocumentNode", "document_id": doc.id}],
    }
    # when given directly, nested dict is not parsed correctly
    client.post(url, json.dumps(data), content_type="application/json")
    assert Message.objects.count() == 1
    message = Message.objects.first()
    doc.refresh_from_db()
    assert doc.attached_object == message
    assert (
        doc.attached_object.get_absolute_url()
        == f"/project/{project_ready.pk}/conversations-new?message-id={message.pk}"
    )


@pytest.mark.django_db
def test_delete_message_with_doc_soft_deletes_doc(
    project_ready, message, sender, request, client
):
    current_site = get_current_site(request)

    doc = baker.make(
        projects_models.Document,
        site=current_site,
        project=project_ready,
        uploaded_by=sender,
        the_link="http://un.site.fr",
    )
    baker.make(DocumentNode, document=doc, position=1, message=message)

    url = reverse(
        "projects-conversations-messages-detail", args=[project_ready.pk, message.pk]
    )
    client.force_login(sender)
    client.delete(url)

    doc.refresh_from_db()
    assert doc.deleted is not None
    assert not message.nodes.exists()


@pytest.mark.django_db
def test_edit_message_removes_doc_soft_deletes_doc(
    project_ready, message, sender, ex_node_dict, request, client
):
    current_site = get_current_site(request)

    doc = baker.make(
        projects_models.Document,
        site=current_site,
        project=project_ready,
        uploaded_by=sender,
        the_link="http://un.site.fr",
    )
    baker.make(DocumentNode, document=doc, position=1, message=message)
    data = {"nodes": [ex_node_dict]}

    url = reverse(
        "projects-conversations-messages-detail", args=[project_ready.pk, message.pk]
    )
    client.force_login(sender)
    client.patch(url, json.dumps(data), content_type="application/json")

    doc.refresh_from_db()
    assert doc.deleted is not None
    assert message.nodes.exists()


@pytest.mark.django_db
def test_edit_message_keeps_doc_restores_it(
    project_ready, message, sender, request, client
):
    current_site = get_current_site(request)

    doc = baker.make(
        projects_models.Document,
        site=current_site,
        project=project_ready,
        uploaded_by=sender,
        the_link="http://un.site.fr",
    )
    baker.make(DocumentNode, document=doc, position=1, message=message)
    data = {
        "nodes": [
            {"position": 1, "type": "DocumentNode", "document_id": doc.id},
            {"position": 2, "type": "MarkdownNode", "text": "I changed that msg"},
        ]
    }

    url = reverse(
        "projects-conversations-messages-detail", args=[project_ready.pk, message.pk]
    )
    client.force_login(sender)
    client.patch(url, json.dumps(data), content_type="application/json")

    doc.refresh_from_db()
    assert doc.deleted is None
    assert doc.attached_object == message
    assert message.nodes.count() == 2


# test envoi message
# test serializer à l'édition du message
# test édition du message
#   - supprime les docs OK
#   - garde le contact
#   - garde la reco
# réactive le projet


#####--- "unread" attribute ---#####
@pytest.mark.django_db
def test_unread_is_zero_if_no_notifications(
    message, project_ready, project_reader, api_client
):
    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])

    api_client.force_login(project_reader)
    response = api_client.get(url)

    assert response.status_code == 200

    assert response.json()[0]["unread"] == 0


@pytest.mark.django_db
def test_unread_counts_unread_notifications(
    message, project_ready, project_reader, api_client
):
    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])

    baker.make(
        Notification,
        actor=project_reader,
        verb=verbs.Conversation.POST_MESSAGE,
        action_object=message,
        public=True,
    )

    api_client.force_login(project_reader)
    response = api_client.get(url)

    assert response.status_code == 200

    assert response.json()[0]["unread"] == 1


@pytest.mark.django_db
def test_unread_does_not_count_read_notifications(
    message, project_ready, project_reader, api_client
):
    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])

    baker.make(
        Notification,
        actor=project_reader,
        verb=verbs.Conversation.POST_MESSAGE,
        action_object=message,
        public=True,
        unread=False,
    )

    api_client.force_login(project_reader)
    response = api_client.get(url)

    assert response.status_code == 200

    assert response.json()[0]["unread"] == 0


#####--- Notifications ---###
@pytest.mark.django_db
def test_post_message_notify_others_and_creates_trace(
    sender, project_ready, request, client
):
    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])

    membership = baker.make(projects_models.ProjectMember, member__is_staff=False)
    project_ready.projectmember_set.add(membership)

    with login(client, user=sender):
        data = {
            "nodes": [
                {
                    "position": 1,
                    "type": "MarkdownNode",
                    "text": "One two this is a test",
                }
            ],
        }

        # when given directly, nested dict is not parsed correctly
        response = client.post(url, json.dumps(data), content_type="application/json")
        assert response.status_code == 201

    # stream and notifications
    message = Message.objects.last()
    actions = action_object_stream(message)
    assert actions.count() == 1
    assert actions[0].verb == verbs.Conversation.POST_MESSAGE

    assert membership.member.notifications.count() == 1


@pytest.mark.django_db
def test_post_message_does_not_notify_poster(sender, project_ready, request, client):
    url = reverse("projects-conversations-messages-list", args=[project_ready.pk])

    with login(client, user=sender):
        data = {
            "nodes": [
                {
                    "position": 1,
                    "type": "MarkdownNode",
                    "text": "One two this is a test",
                }
            ],
        }

        # when given directly, nested dict is not parsed correctly
        response = client.post(url, json.dumps(data), content_type="application/json")
        assert response.status_code == 201

    # stream and notifications
    assert sender.notifications.count() == 0


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


@pytest.mark.django_db
def test_gather_notifications_for_message(message):
    annotations = gather_annotations_for_message_notification(message)

    assert annotations["documents"]["count"] == 0
    assert annotations["contacts"]["count"] == 0
    assert annotations["recommendations"]["count"] == 0


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


@pytest.mark.django_db
def test_message_notification_is_filled_with_metadata_upon_creation(
    project_ready, sender, request, message
):
    membership = baker.make(projects_models.ProjectMember, member__is_staff=False)
    project_ready.projectmember_set.add(membership)

    signals.message_posted.send(
        sender=test_message_notification_is_filled_with_metadata_upon_creation,
        message=message,
    )

    notification = Notification.objects.last()
    assert notification

    assert "annotations" in notification.data.keys()
