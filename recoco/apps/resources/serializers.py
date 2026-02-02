from django.contrib.auth import models as auth_models
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from taggit.serializers import TagListSerializerField, TaggitSerializer

from recoco.rest_api.serializers import BaseSerializerMixin

from ..addressbook.models import Contact
from ..geomatics.models import Department
from .models import Category, Resource, ResourceAddon


class ResourceCreatorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = auth_models.User

        fields = [
            "first_name",
            "last_name",
        ]


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category

        fields = [
            "id",
            "name",
        ]


class ResourceSerializer(
    BaseSerializerMixin, TaggitSerializer, serializers.HyperlinkedModelSerializer
):
    class Meta:
        model = Resource
        fields = [
            "id",
            "title",
            "subtitle",
            "tags",
            "status",
            "web_url",
            "embeded_url",
            "has_dsresource",
            "category",
            "support_orga",
            "departments",
            "created_by",
        ]
        read_only_fields = [
            "created_by",
        ]

    web_url = serializers.URLField(source="get_absolute_url", read_only=True)
    embeded_url = serializers.URLField(source="get_embeded_url", read_only=True)
    tags = TagListSerializerField()
    created_by = ResourceCreatorSerializer(read_only=True, many=False)
    category = CategorySerializer(read_only=True)
    has_dsresource = serializers.BooleanField(read_only=True, default=False)
    departments = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects, many=True
    )


class ResourceDetailSerializer(ResourceSerializer):
    class Meta:
        model = Resource
        fields = [
            "id",
            "title",
            "subtitle",
            "tags",
            "status",
            "created_on",
            "created_by",
            "updated_on",
            "web_url",
            "embeded_url",
            "has_dsresource",
            "category",
            "contacts",
            "departments",
            "content",
        ]
        read_only_fields = [
            "created_on",
            "updated_on",
            "created_by",
        ]

    contacts = serializers.PrimaryKeyRelatedField(queryset=Contact.objects, many=True)


class ResourceWritableSerializer(ResourceDetailSerializer):
    category = PrimaryKeyRelatedField(queryset=Category.objects)

    def save(self, **kwargs):
        return super().save(
            created_by=self.current_user, sites=[self.current_site], **kwargs
        )


class ResourceURIImportSerializer(serializers.Serializer):
    uri = serializers.URLField()


class ResourceWebhookSerializer(
    BaseSerializerMixin, TaggitSerializer, serializers.HyperlinkedModelSerializer
):
    class Meta:
        model = Resource
        fields = (
            "id",
            "title",
            "subtitle",
            "tags",
            "status",
        )

    tags = TagListSerializerField()


class ResourceAddonSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ResourceAddon
        fields = [
            "id",
            "nature",
            "recommendation",
            "data",
            "enabled",
        ]

    def save(self, **kwargs):
        if recommendation := self.validated_data.get("recommendation"):
            if not recommendation.resource:
                raise serializers.ValidationError(
                    "Recommendation must be linked to a resource."
                )
            if recommendation.site != self.current_site:
                raise serializers.ValidationError(
                    "Recommendation must be linked to the current site."
                )

        return super().save(**kwargs)
