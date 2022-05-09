from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from generic_relations.relations import GenericRelatedField
from notifications import models as notifications_models
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers
from urbanvitaliz.apps.geomatics.serializers import CommuneSerializer
from urbanvitaliz.apps.reminders.serializers import MailSerializer

from .models import Project, Task, TaskFollowup


class UserSerializer(serializers.HyperlinkedModelSerializer):
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

    switchtenders = UserSerializer(read_only=True, many=True)
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

    who = UserSerializer(read_only=True, many=False)


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
            "notifications",
        ]

    created_by = UserSerializer(read_only=True, many=False)
    reminders = MailSerializer(read_only=True, many=True)

    notifications = serializers.SerializerMethodField()

    def get_notifications(self, obj):
        request = self.context.get("request")

        followup_ct = ContentType.objects.get_for_model(TaskFollowup)

        followup_ids = list(obj.followups.all().values_list("id", flat=True))
        unread_notifications = request.user.notifications.filter(
            action_object_content_type=followup_ct.pk,
            action_object_object_id__in=followup_ids,
        ).unread()

        return {
            "count": unread_notifications.count(),
        }


class TaskNotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notifications_models.Notification
        fields = ["id", "actor", "verb", "action_object", "timestamp"]

    actor = GenericRelatedField({auth_models.User: UserSerializer()})
    action_object = GenericRelatedField(
        {Task: TaskSerializer(), TaskFollowup: TaskFollowupSerializer()}
    )
