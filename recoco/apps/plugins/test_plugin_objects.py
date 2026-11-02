"""Plugin objects stored in core tables shared by every tenant (conversation
nodes, actstream actions, notifications) only show where the plugin is enabled.
"""

import json

import pytest
from actstream import action
from actstream.models import Action
from django.urls import reverse
from model_bakery import baker
from notifications.signals import notify
from rest_framework import serializers

from recoco import verbs
from recoco.apps.communication import digests
from recoco.apps.conversations.models import MarkdownNode, Message
from recoco.apps.conversations.serializers import NodePolymorphicSerializer
from recoco.apps.conversations.utils import (
    gather_annotations_for_message_notification,
)
from recoco.utils import login

from .testing import PLUGIN
from .testing.plugin_testapp.models import Note, NoteNode
from .utils import exclude_disabled_plugin_objects


class NoteNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteNode
        fields = ("position", "note")


@pytest.fixture
def note_node_type(monkeypatch):
    # Like plugins do in their AppConfig.ready()
    monkeypatch.setitem(
        NodePolymorphicSerializer.model_serializer_mapping,
        NoteNode,
        NoteNodeSerializer,
    )


@pytest.fixture
def note(plugin_tables, current_site):
    return Note.objects.create(site=current_site, title="from the plugin")


@pytest.fixture
def mixed_message(project_ready, project_editor, note):
    message = baker.make(Message, project=project_ready, posted_by=project_editor)
    MarkdownNode.objects.create(message=message, position=0, text="core")
    NoteNode.objects.create(message=message, position=1, note=note)
    return message


@pytest.fixture
def plugin_message(project_ready, project_editor, note):
    message = baker.make(Message, project=project_ready, posted_by=project_editor)
    NoteNode.objects.create(message=message, position=0, note=note)
    return message


def messages_url(project):
    return reverse("projects-conversations-messages-list", args=[project.pk])


@pytest.mark.django_db
def test_exclude_disabled_plugin_objects_on_actions(
    enabled_plugins, project_ready, project_editor, note
):
    action.send(
        project_editor, verb="plugin verb", action_object=note, target=project_ready
    )
    action.send(project_editor, verb="core verb", action_object=project_ready)

    def visible_verbs():
        return set(
            exclude_disabled_plugin_objects(
                Action.objects.all(),
                "action_object_content_type",
                "target_content_type",
            ).values_list("verb", flat=True)
        )

    enabled_plugins(PLUGIN)
    assert visible_verbs() == {"plugin verb", "core verb"}

    enabled_plugins()
    # The core action has no target: a null content type must not be excluded
    assert visible_verbs() == {"core verb"}


# --- conversations API ---


@pytest.mark.parametrize(
    "enabled,expected_nodes",
    [
        ((PLUGIN,), {"mixed": ["MarkdownNode", "NoteNode"], "plugin": ["NoteNode"]}),
        # The message made of plugin nodes only is gone
        ((), {"mixed": ["MarkdownNode"]}),
    ],
)
@pytest.mark.django_db
def test_plugin_nodes_only_listed_where_plugin_enabled(
    client,
    site_with_enabled_plugins,
    note_node_type,
    project_ready,
    project_editor,
    mixed_message,
    plugin_message,
    enabled,
    expected_nodes,
):
    site_with_enabled_plugins(enabled)
    with login(client, user=project_editor):
        response = client.get(messages_url(project_ready))

    assert response.status_code == 200
    names = {mixed_message.pk: "mixed", plugin_message.pk: "plugin"}
    assert {
        names[m["id"]]: [n["type"] for n in m["nodes"]] for m in response.json()
    } == expected_nodes


@pytest.mark.django_db
def test_messages_without_nodes_still_listed_where_plugin_disabled(
    client, site_without_plugins, project_ready, project_editor
):
    # Soft deleted messages have no node left
    message = baker.make(Message, project=project_ready, posted_by=project_editor)
    with login(client, user=project_editor):
        response = client.get(messages_url(project_ready))

    assert [m["id"] for m in response.json()] == [message.pk]


@pytest.mark.parametrize("enabled,status_code", [((PLUGIN,), 201), ((), 400)])
@pytest.mark.django_db
def test_post_plugin_node(
    client,
    site_with_enabled_plugins,
    note_node_type,
    project_ready,
    project_editor,
    note,
    enabled,
    status_code,
):
    site_with_enabled_plugins(enabled)
    data = {"nodes": [{"type": "NoteNode", "position": 0, "note": note.pk}]}
    with login(client, user=project_editor):
        response = client.post(
            messages_url(project_ready),
            json.dumps(data),
            content_type="application/json",
        )

    assert response.status_code == status_code
    assert NoteNode.objects.count() == (1 if status_code == 201 else 0)


@pytest.mark.parametrize("enabled,status_code", [((PLUGIN,), 200), ((), 400)])
@pytest.mark.django_db
def test_edit_message_with_plugin_nodes(
    client,
    site_with_enabled_plugins,
    note_node_type,
    project_editor,
    mixed_message,
    enabled,
    status_code,
):
    # Editing replaces every node: it can't happen where some are hidden
    site_with_enabled_plugins(enabled)
    data = {"nodes": [{"type": "MarkdownNode", "position": 0, "text": "edited"}]}
    with login(client, user=project_editor):
        response = client.patch(
            reverse(
                "projects-conversations-messages-detail",
                args=[mixed_message.project_id, mixed_message.pk],
            ),
            json.dumps(data),
            content_type="application/json",
        )

    assert response.status_code == status_code
    if status_code == 400:
        assert NoteNode.objects.filter(message=mixed_message).exists()


# --- message digests ---


@pytest.fixture
def recipient(project_ready):
    recipient = baker.make("auth.User")
    project_ready.members.add(recipient)
    return recipient


@pytest.fixture
def send_email(mocker):
    return mocker.patch.object(digests, "send_email")


def notify_messages(messages, recipient):
    for message in messages:
        notify.send(
            sender=message.posted_by,
            recipient=[recipient],
            verb=verbs.Conversation.POST_MESSAGE,
            action_object=message,
            target=message.project,
            site=message.project.sites.first(),
            annotations=gather_annotations_for_message_notification(message),
        )


@pytest.mark.parametrize(
    "enabled,title_count,linked_message",
    [
        # The message made of plugin nodes only is left out
        ((), "1 nouveau message", "mixed"),
        # Plugin nodes are part of their message, never the first object
        ((PLUGIN,), "2 nouveaux messages", "plugin"),
    ],
)
@pytest.mark.django_db
def test_msg_digest_with_plugin_nodes(
    send_email,
    enabled_plugins,
    current_site,
    project_ready,
    recipient,
    mixed_message,
    plugin_message,
    enabled,
    title_count,
    linked_message,
):
    notify_messages([plugin_message, mixed_message], recipient)

    enabled_plugins(*enabled)
    digests.send_msg_digest_by_user_and_project(project_ready, recipient, current_site)

    params = send_email.call_args.kwargs["params"]
    assert params["title_count"] == title_count
    assert params["first_object"] is None
    message = {"mixed": mixed_message, "plugin": plugin_message}[linked_message]
    assert f"message-id={message.pk}" in params["message_url"]


@pytest.mark.django_db
def test_no_msg_digest_for_plugin_only_messages_where_plugin_disabled(
    send_email, enabled_plugins, current_site, project_ready, recipient, plugin_message
):
    notify_messages([plugin_message], recipient)

    enabled_plugins()
    sent = digests.send_msg_digest_by_user_and_project(
        project_ready, recipient, current_site
    )

    assert sent == 0
    send_email.assert_not_called()
