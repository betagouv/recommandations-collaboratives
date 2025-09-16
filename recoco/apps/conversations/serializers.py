# serializers.py
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

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
