from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from generic_relations.relations import GenericRelatedField
from notifications import models as notifications_models
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers
from urbanvitaliz.apps.geomatics.serializers import CommuneSerializer
from urbanvitaliz.apps.home.serializers import UserSerializer
from urbanvitaliz.apps.reminders import models as reminders_models
from urbanvitaliz.apps.reminders.serializers import MailSerializer

from .models import Project, Task, TaskFollowup
from .utils import create_reminder


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
        fields = [
            "id",
            "status",
            "status_txt",
            "comment",
            "who",
            "timestamp",
            "task_id",
            "who_id",
        ]
        read_only_fields = ["who"]
        extra_kwargs = {"task_id": {"write_only": True}, "who_id": {"write_only": True}}

    who = UserSerializer(read_only=True, many=False)

    task_id = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, queryset=Task.objects
    )
    who_id = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, queryset=auth_models.User.objects
    )

    def create(self, validated_data):
        followup = TaskFollowup(
            status=validated_data.get("status", None),
            comment=validated_data["comment"],
        )
        followup.task = validated_data["task_id"]
        followup.who = validated_data["who_id"]

        followup.save()

        task = followup.task

        if followup.status not in [Task.ALREADY_DONE, Task.NOT_INTERESTED, Task.DONE]:
            create_reminder(
                7 * 6, task, followup.who, origin=reminders_models.Mail.UNKNOWN
            )

        return followup


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
            "followups_count",
            "comments_count",
        ]

    created_by = UserSerializer(read_only=True, many=False)
    reminders = MailSerializer(read_only=True, many=True)

    notifications = serializers.SerializerMethodField()
    followups_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

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

    def get_followups_count(self, obj):
        return obj.followups.count()

    def get_comments_count(self, obj):
        return obj.followups.exclude(comment="").count()

    # FIXME : We should not send all the tasks to non switchtender users (filter queryset on current_user)


class TaskNotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notifications_models.Notification
        fields = ["id", "actor", "verb", "action_object", "timestamp"]

    actor = GenericRelatedField({auth_models.User: UserSerializer()})
    action_object = GenericRelatedField(
        {Task: TaskSerializer(), TaskFollowup: TaskFollowupSerializer()}
    )
