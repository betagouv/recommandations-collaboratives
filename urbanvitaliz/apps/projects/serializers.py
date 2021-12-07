from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "status", "created_on", "updated_on", "org_name"]
