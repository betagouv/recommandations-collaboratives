from django.contrib.auth import models as auth_models
from rest_framework import serializers

from .models import Project


class SwitchtenderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = auth_models.User

        fields = ["username", "first_name", "last_name", "email"]


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "status",
            "created_on",
            "updated_on",
            "org_name",
            "switchtender",
        ]

    switchtender = SwitchtenderSerializer(read_only=True)
