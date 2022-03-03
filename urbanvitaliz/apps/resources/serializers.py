from rest_framework import serializers

from .models import Resource


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = [
            "id",
            "title",
            "subtitle",
            "status",
            "created_on",
            "updated_on",
        ]
