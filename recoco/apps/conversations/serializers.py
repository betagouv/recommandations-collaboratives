# serializers.py
from actstream.models import Action
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from recoco.apps.home.serializers import UserSerializer
from recoco.apps.projects.models import Project
from recoco.apps.tasks.models import Task

from .models import (
    ContactNode,
    DocumentNode,
    MarkdownNode,
    Message,
    Node,
    RecommendationNode,
)


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ("position",)


class MarkdownNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkdownNode
        fields = (
            "position",
            "text",
        )


class RecommendationNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationNode
        fields = ("position", "text", "recommendation_id")


class ContactNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactNode
        fields = (
            "position",
            "contact_id",
        )


class DocumentNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentNode
        fields = (
            "position",
            "document_id",
        )


class NodePolymorphicSerializer(PolymorphicSerializer):
    resource_type_field_name = "type"

    model_serializer_mapping = {
        Node: NodeSerializer,
        MarkdownNode: MarkdownNodeSerializer,
        RecommendationNode: RecommendationNodeSerializer,
        ContactNode: ContactNodeSerializer,
        DocumentNode: DocumentNodeSerializer,
    }


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "created", "modified", "posted_by", "in_reply_to", "nodes")

    nodes = NodePolymorphicSerializer(many=True)

    def create(self, validated_data):
        nodes_data = validated_data.pop("nodes")
        message = super().create(**validated_data)
        for node_data in nodes_data:
            message.nodes.add(NodePolymorphicSerializer.create(**node_data))
        return message


class ActivityUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "model",
            "id",
        )

    model = serializers.ReadOnlyField(default="User")


class ActivityProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("model", "id", "name")

    model = serializers.ReadOnlyField(default="Project")


class ActivityTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("model", "id", "intent")

    model = serializers.ReadOnlyField(default="Task")


class GenericRelatedField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, User):
            return ActivityUserSerializer(value).data

        if isinstance(value, Project):
            return ActivityProjectSerializer(value).data

        if isinstance(value, Task):
            return ActivityTaskSerializer(value).data

        # Not found - return string.
        return str(value)


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ("id", "timestamp", "actor", "action_object", "verb")

    actor = GenericRelatedField(read_only=True)
    action_object = GenericRelatedField(read_only=True)


class ParticipantSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["last_login", "id"]
