from django.contrib.auth import models as auth_models
from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from .models import Category, Resource


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


class ResourceSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
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
        ]
        read_only_fields = [
            "created_on",
            "updated_on",
            "created_by",
        ]

    web_url = serializers.URLField(source="get_absolute_url", read_only=True)
    embeded_url = serializers.URLField(source="get_embeded_url", read_only=True)
    tags = TagListSerializerField()
    created_by = ResourceCreatorSerializer(read_only=True, many=False)
    category = CategorySerializer(read_only=True)
    has_dsresource = serializers.BooleanField(read_only=True, default=False)


class ResourceURIImportSerializer(serializers.Serializer):
    uri = serializers.URLField()
