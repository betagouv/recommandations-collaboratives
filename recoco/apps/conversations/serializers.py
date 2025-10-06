# serializers.py
from actstream.models import Action
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from recoco.apps.home.serializers import UserSerializer
from recoco.apps.projects.models import Document, Project
from recoco.apps.tasks.models import Task

from ..addressbook.models import Contact
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

    recommendation_id = serializers.PrimaryKeyRelatedField(
        source="recommendation", queryset=Task.on_site
    )


class ContactNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactNode
        fields = (
            "position",
            "contact_id",
        )

    contact_id = serializers.PrimaryKeyRelatedField(
        source="contact", queryset=Contact.on_site
    )


class DocumentNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentNode
        fields = (
            "position",
            "document_id",
        )

    document_id = serializers.PrimaryKeyRelatedField(
        source="document", queryset=Document.on_site.all()
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
        fields = (
            "in_reply_to",
            "nodes",
            "id",
            "posted_by",
            "created",
            "modified",
            "unread",
            "deleted",
        )
        read_only_fields = (
            "id",
            "posted_by",
            "created",
            "modified",
            "unread",
            "deleted",
        )

    unread = serializers.IntegerField(read_only=True)

    nodes = NodePolymorphicSerializer(many=True)

    def validate_nodes(self, node_list):
        if len(node_list) == 0:
            raise serializers.ValidationError("A message must have at least one node.")
        return node_list

    def create(self, validated_data):
        nodes_data = validated_data.pop("nodes")
        message = Message.objects.create(**validated_data)
        with transaction.atomic():
            message.save()
            for node_data in nodes_data:
                node_data["message_id"] = message.id
                NodePolymorphicSerializer().create(node_data)
        return message

    def update(self, instance, validated_data):
        nodes_data = validated_data.pop("nodes")

        with transaction.atomic():
            super().update(instance, validated_data)
            old_nodes = [*instance.nodes.all()]

            for node in old_nodes:
                node.delete()
                # cannot do queryset.delete directly otherwise polymorphism delete.CASCADE is not applied
                # and it fails

            # order of loops is important for document nodes side effects

            for node_data in nodes_data:
                node_data["message_id"] = instance.id
                NodePolymorphicSerializer().create(node_data)

        return instance


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
