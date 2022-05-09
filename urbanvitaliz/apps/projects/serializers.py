from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers
from urbanvitaliz.apps.geomatics.serializers import CommuneSerializer
from urbanvitaliz.apps.reminders.serializers import MailSerializer

from .models import Project, Task, TaskFollowup


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
            "switchtenders",
            "is_switchtender",
            "commune",
            "notifications",
        ]

    switchtenders = SwitchtenderSerializer(read_only=True, many=True)
    is_switchtender = serializers.SerializerMethodField()

    def get_is_switchtender(self, obj):
        request = self.context.get("request")
        return request.user in obj.switchtenders.all()

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


class TaskFollowupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaskFollowup
        fields = ["id", "status", "status_txt", "comment", "who", "timestamp"]

    who = SwitchtenderSerializer(read_only=True, many=False)


class TaskSerializer(serializers.HyperlinkedModelSerializer, OrderedModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "status",
            "visited",
            "public",
            "priority",
            "order",
            "created_on",
            "updated_on",
            "created_by",
            "intent",
            "content",
            "reminders",
            "resource_id",
        ]

    created_by = SwitchtenderSerializer(read_only=True, many=False)
    reminders = MailSerializer(read_only=True, many=True)
