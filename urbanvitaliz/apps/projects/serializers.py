from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from urbanvitaliz.apps.geomatics.serializers import CommuneSerializer

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
            "commune",
            "notifications",
        ]

    switchtender = SwitchtenderSerializer(read_only=True)
    commune = CommuneSerializer(read_only=True)

    notifications = serializers.SerializerMethodField()

    def get_notifications(self, obj):
        request = self.context.get("request")
        notifications = request.user.notifications

        project_ct = ContentType.objects.get_for_model(obj)

        switchtender_group = auth_models.Group.objects.get(name="switchtender")
        switchtenders = switchtender_group.user_set.values_list("id", flat=True)
        switchtenders = [int(switchtender) for switchtender in switchtenders]

        unread_notifications = notifications.filter(
            target_content_type=project_ct.pk, target_object_id=obj.pk
        ).unread()

        return {
            "count": unread_notifications.count(),
            "has_collaborator_activity": unread_notifications.exclude(
                actor_object_id__in=switchtenders
            ).exists(),
        }
