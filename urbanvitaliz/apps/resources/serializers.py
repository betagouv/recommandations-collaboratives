from rest_framework import serializers

from .models import Resource


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
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
        ]

    web_url = serializers.URLField(source="get_absolute_url", read_only=True)
