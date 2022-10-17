from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Resource


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
            "updated_on",
            "web_url",
            "embeded_url",
        ]

    web_url = serializers.URLField(source="get_absolute_url", read_only=True)
    embeded_url = serializers.URLField(source="get_embeded_url", read_only=True)
    tags = TagListSerializerField()
