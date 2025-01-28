from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from generic_relations.relations import GenericRelatedField
from notifications import models as notifications_models
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers

from recoco.apps.addressbook.serializers import NestedContactSerializer
from recoco.apps.demarches_simplifiees.serializers import DSFolderSerializer
from recoco.apps.home.serializers import UserSerializer
from recoco.apps.projects.serializers import DocumentSerializer, TopicSerializer
from recoco.apps.projects.utils import get_collaborators_for_project
from recoco.apps.resources.serializers import ResourceSerializer
from recoco.rest_api.serializers import BaseSerializerMixin

from .models import Task, TaskFollowup


class TaskFollowupCreateSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = TaskFollowup
        fields = [
            "id",
            "status",
            "contact",
            "status",
            "comment",
            "who",
            "task",
        ]
        read_only_fields = [
            "who",
            "task",
        ]

    def create(self, validated_data):
        followup = super().create(
            validated_data
            | {
                "who": self.current_user,
                "task_id": self.context.get("task_id"),
            }
        )

        task = followup.task
        project = task.project

        # update activity flags and states
        if followup.who in get_collaborators_for_project(project):
            project.last_members_activity_at = timezone.now()
            if project.inactive_since:
                project.reactivate()
            project.save()

        return followup


class TaskFollowupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFollowup
        fields = [
            "id",
            "status",
            "status",
            "status_txt",
            "comment",
            "who",
            "contact",
            "timestamp",
        ]
        # read_only_fields = fields

    who = UserSerializer(read_only=True, many=False)
    contact = NestedContactSerializer(read_only=True)


class TaskSerializer(
    BaseSerializerMixin, serializers.HyperlinkedModelSerializer, OrderedModelSerializer
):
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
            "document",
            "resource_id",
            "resource",
            "notifications",
            "followups_count",
            "comments_count",
            "topic",
            "site",
            "ds_folder",
        ]
        read_only_fields = ["created_on", "updated_on", "created_by"]

    created_by = UserSerializer(read_only=True, many=False)

    document = DocumentSerializer(read_only=True, many=True)

    resource = ResourceSerializer(read_only=True, many=False)

    notifications = serializers.SerializerMethodField()
    followups_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    topic = TopicSerializer(read_only=True)
    ds_folder = DSFolderSerializer(read_only=True)

    site = serializers.SerializerMethodField()

    def get_site(self, obj):
        return {"name": obj.site.name, "id": obj.site.id}

    def get_notifications(self, obj):
        request = self.context.get("request")

        followup_ct = ContentType.objects.get_for_model(TaskFollowup)

        followup_ids = list(obj.followups.all().values_list("id", flat=True))

        unread_notifications = (
            notifications_models.Notification.on_site.filter(recipient=request.user)
            .filter(
                action_object_content_type=followup_ct.pk,
                action_object_object_id__in=followup_ids,
            )
            .unread()
        )

        return {
            "count": unread_notifications.count(),
        }

    def get_followups_count(self, obj):
        return obj.followups.count()

    def get_comments_count(self, obj):
        return obj.followups.exclude(comment="").count()

    # FIXME : We should not send all the tasks to non switchtender users (filter
    # queryset on current_user)

    def save(self, **kwargs):
        return super().save(
            created_by=self.current_user, site=self.current_site, **kwargs
        )


class TaskNotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notifications_models.Notification
        fields = ["id", "actor", "verb", "action_object", "timestamp"]

    actor = GenericRelatedField({auth_models.User: UserSerializer()})
    action_object = GenericRelatedField(
        {Task: TaskSerializer(), TaskFollowup: TaskFollowupSerializer()}
    )


# eof
