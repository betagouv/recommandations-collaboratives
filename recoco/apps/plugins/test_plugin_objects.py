"""Plugin objects stored in core tables shared by every tenant (conversation
nodes, actstream actions, notifications) only show where the plugin is enabled.
"""

import json
from io import StringIO

import pytest
from actstream import action
from actstream.models import Action
from django.core.management import call_command
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
from recoco.apps.home.models import SiteConfiguration
from recoco.utils import login

from .resolvers import set_enabled_plugins
from .testing.plugin_testapp.models import Note, NoteNode
from .utils import (
    exclude_disabled_plugin_objects,
    get_disabled_plugin_app_labels,
    is_disabled_plugin_model,
)

PLUGIN = "plugin_testapp"


class NoteNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteNode
        fields = ("position", "note")


@pytest.fixture
def plugin_tables(db):
    call_command("migrate_plugins", PLUGIN, verbosity=0, stdout=StringIO())


@pytest.fixture
def enabled_plugins():
    def enable(*plugins):
        set_enabled_plugins(list(plugins))

    yield enable
    set_enabled_plugins([])


@pytest.fixture
def note_node_type(monkeypatch):
    # Like plugins do in their AppConfig.ready()
    monkeypatch.setitem(
        NodePolymorphicSerializer.model_serializer_mapping,
        NoteNode,
        NoteNodeSerializer,
    )


@pytest.fixture
def site_plugins(current_site):
    def enable(*plugins):
        return baker.make(
            SiteConfiguration, site=current_site, enabled_plugins=list(plugins)
        )

    return enable


@pytest.fixture
def note(plugin_tables, current_site):
    return Note.objects.create(site=current_site, title="from the plugin")


@pytest.fixture
def sender(project_editor):
    return project_editor


@pytest.fixture
def mixed_message(project_ready, sender, note):
    message = baker.make(Message, project=project_ready, posted_by=sender)
    MarkdownNode.objects.create(message=message, position=0, text="core")
    NoteNode.objects.create(message=message, position=1, note=note)
    return message


@pytest.fixture
def plugin_message(project_ready, sender, note):
    message = baker.make(Message, project=project_ready, posted_by=sender)
    NoteNode.objects.create(message=message, position=0, note=note)
    return message


def messages_url(project):
    return reverse("projects-conversations-messages-list", args=[project.pk])


def message_url(message):
    return reverse(
        "projects-conversations-messages-detail",
        args=[message.project_id, message.pk],
    )


# --- helpers ---


def test_disabled_plugin_app_labels_follow_enabled_plugins(enabled_plugins):
    enabled_plugins()
    assert PLUGIN in get_disabled_plugin_app_labels()
    assert is_disabled_plugin_model(NoteNode)

    enabled_plugins(PLUGIN)
    assert PLUGIN not in get_disabled_plugin_app_labels()
    assert not is_disabled_plugin_model(NoteNode)


def test_core_models_are_never_disabled(enabled_plugins):
    enabled_plugins()
    assert not is_disabled_plugin_model(MarkdownNode)


@pytest.mark.django_db
def test_exclude_disabled_plugin_objects_on_actions(
    enabled_plugins, project_ready, sender, note
):
    action.send(sender, verb="plugin verb", action_object=note, target=project_ready)
    action.send(sender, verb="core verb", action_object=project_ready)
    actions = Action.objects.all()

    enabled_plugins(PLUGIN)
    assert set(
        exclude_disabled_plugin_objects(
            actions, "action_object_content_type", "target_content_type"
        ).values_list("verb", flat=True)
    ) == {"plugin verb", "core verb"}

    enabled_plugins()
    # The core action has no target: a null content type must not be excluded
    assert list(
        exclude_disabled_plugin_objects(
            actions, "action_object_content_type", "target_content_type"
        ).values_list("verb", flat=True)
    ) == ["core verb"]


# --- conversations API ---


@pytest.mark.django_db
def test_plugin_nodes_listed_where_plugin_enabled(
    client,
    site_plugins,
    note_node_type,
    project_ready,
    sender,
    mixed_message,
    plugin_message,
):
    site_plugins(PLUGIN)
    with login(client, user=sender):
        response = client.get(messages_url(project_ready))

    assert response.status_code == 200
    nodes_by_message = {m["id"]: m["nodes"] for m in response.json()}
    assert [n["type"] for n in nodes_by_message[mixed_message.pk]] == [
        "MarkdownNode",
        "NoteNode",
    ]
    assert [n["type"] for n in nodes_by_message[plugin_message.pk]] == ["NoteNode"]


@pytest.mark.django_db
def test_plugin_nodes_hidden_where_plugin_disabled(
    client,
    site_plugins,
    note_node_type,
    project_ready,
    sender,
    mixed_message,
    plugin_message,
):
    site_plugins()
    with login(client, user=sender):
        response = client.get(messages_url(project_ready))

    assert response.status_code == 200
    nodes_by_message = {m["id"]: m["nodes"] for m in response.json()}
    # Only the core node is left; the message made of plugin nodes only is gone
    assert list(nodes_by_message) == [mixed_message.pk]
    assert [n["type"] for n in nodes_by_message[mixed_message.pk]] == ["MarkdownNode"]


@pytest.mark.django_db
def test_messages_without_nodes_still_listed_where_plugin_disabled(
    client, site_plugins, project_ready, sender
):
    # Soft deleted messages have no node left
    message = baker.make(Message, project=project_ready, posted_by=sender)
    site_plugins()
    with login(client, user=sender):
        response = client.get(messages_url(project_ready))

    assert [m["id"] for m in response.json()] == [message.pk]


@pytest.mark.parametrize("enabled,status_code", [((PLUGIN,), 201), ((), 400)])
@pytest.mark.django_db
def test_post_plugin_node(
    client,
    site_plugins,
    note_node_type,
    project_ready,
    sender,
    note,
    enabled,
    status_code,
):
    site_plugins(*enabled)
    data = {"nodes": [{"type": "NoteNode", "position": 0, "note": note.pk}]}
    with login(client, user=sender):
        response = client.post(
            messages_url(project_ready),
            json.dumps(data),
            content_type="application/json",
        )

    assert response.status_code == status_code
    assert NoteNode.objects.count() == (1 if status_code == 201 else 0)


@pytest.mark.django_db
def test_cannot_edit_message_with_hidden_plugin_nodes(
    client, site_plugins, note_node_type, sender, mixed_message
):
    site_plugins()
    data = {"nodes": [{"type": "MarkdownNode", "position": 0, "text": "edited"}]}
    with login(client, user=sender):
        response = client.patch(
            message_url(mixed_message),
            json.dumps(data),
            content_type="application/json",
        )

    assert response.status_code == 400
    assert NoteNode.objects.filter(message=mixed_message).exists()


@pytest.mark.django_db
def test_can_edit_message_with_plugin_nodes_where_plugin_enabled(
    client, site_plugins, note_node_type, sender, mixed_message
):
    site_plugins(PLUGIN)
    data = {"nodes": [{"type": "MarkdownNode", "position": 0, "text": "edited"}]}
    with login(client, user=sender):
        response = client.patch(
            message_url(mixed_message),
            json.dumps(data),
            content_type="application/json",
        )

    assert response.status_code == 200


# --- message digests ---


@pytest.fixture
def recipient(project_ready):
    recipient = baker.make("auth.User")
    project_ready.members.add(recipient)
    return recipient


def notify_messages(messages, sender, recipient, site, project):
    for message in messages:
        notify.send(
            sender=sender,
            recipient=[recipient],
            verb=verbs.Conversation.POST_MESSAGE,
            action_object=message,
            target=project,
            site=site,
            annotations=gather_annotations_for_message_notification(message),
        )


@pytest.mark.django_db
def test_msg_digest_leaves_out_plugin_nodes_where_plugin_disabled(
    monkeypatch,
    enabled_plugins,
    current_site,
    project_ready,
    sender,
    recipient,
    mixed_message,
    plugin_message,
):
    notify_messages(
        [plugin_message, mixed_message], sender, recipient, current_site, project_ready
    )
    sent = []
    monkeypatch.setattr(
        digests, "send_email", lambda *args, **kwargs: sent.append(kwargs["params"])
    )

    enabled_plugins()
    digests.send_msg_digest_by_user_and_project(project_ready, recipient, current_site)

    # The message made of plugin nodes only is left out
    [digest] = sent
    assert digest["title_count"] == "1 nouveau message"
    assert digest["first_object"] is None
    assert f"message-id={mixed_message.pk}" in digest["message_url"]


@pytest.mark.django_db
def test_no_msg_digest_for_plugin_only_messages_where_plugin_disabled(
    monkeypatch,
    enabled_plugins,
    current_site,
    project_ready,
    sender,
    recipient,
    plugin_message,
):
    notify_messages([plugin_message], sender, recipient, current_site, project_ready)
    sent = []
    monkeypatch.setattr(
        digests, "send_email", lambda *args, **kwargs: sent.append(kwargs["params"])
    )

    enabled_plugins()
    assert (
        digests.send_msg_digest_by_user_and_project(
            project_ready, recipient, current_site
        )
        == 0
    )
    assert sent == []


@pytest.mark.django_db
def test_msg_digest_counts_plugin_nodes_as_messages_where_plugin_enabled(
    monkeypatch,
    enabled_plugins,
    current_site,
    project_ready,
    sender,
    recipient,
    mixed_message,
    plugin_message,
):
    notify_messages(
        [plugin_message, mixed_message], sender, recipient, current_site, project_ready
    )
    sent = []
    monkeypatch.setattr(
        digests, "send_email", lambda *args, **kwargs: sent.append(kwargs["params"])
    )

    enabled_plugins(PLUGIN)
    digests.send_msg_digest_by_user_and_project(project_ready, recipient, current_site)

    # Plugin nodes are part of their message, never the digest's first object
    [digest] = sent
    assert digest["title_count"] == "2 nouveaux messages"
    assert digest["first_object"] is None
    assert f"message-id={plugin_message.pk}" in digest["message_url"]
