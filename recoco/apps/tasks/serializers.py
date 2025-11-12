from typing import Any

from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from generic_relations.relations import GenericRelatedField
from notifications import models as notifications_models
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers

from recoco.apps.addressbook.models import Contact
from recoco.apps.addressbook.serializers import NestedContactSerializer
from recoco.apps.demarches_simplifiees.serializers import DSFolderSerializer
from recoco.apps.home.serializers import UserSerializer
from recoco.apps.projects.serializers import DocumentSerializer, TopicSerializer
from recoco.apps.projects.utils import reactivate_if_necessary
from recoco.apps.resources.models import Resource
from recoco.apps.resources.serializers import (
    ResourceSerializer,
    ResourceWebhookSerializer,
)
from recoco.rest_api.serializers import BaseSerializerMixin

from .models import Task, TaskFollowup


class TaskFollowupCreateUpdateSerializer(
    BaseSerializerMixin, serializers.ModelSerializer
):
    class Meta:
        model = TaskFollowup
        fields = [
            "id",
            "status",
            "contact",
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
        self._update_activity_flags_and_states(followup)
        return followup

    def update(self, instance, validated_data):
        followup = super().update(instance, validated_data)
        self._update_activity_flags_and_states(followup)
        return followup

    def _update_activity_flags_and_states(self, followup):
        reactivate_if_necessary(followup.task.project, followup.who)


class TaskFollowupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFollowup
        fields = [
            "id",
            "status",
            "status_txt",
            "comment",
            "who",
            "contact",
            "timestamp",
        ]

    who = UserSerializer(read_only=True, many=False)
    contact = NestedContactSerializer(read_only=True)


class TaskSerializer(BaseSerializerMixin, OrderedModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "status",
            "visited",
            "public",
            "priority",
            "order",
            "intent",
            "content",
            "contact",
            "contact_id",
            "created_on",
            "updated_on",
            "created_by",
            "document",
            "resource",
            "resource_id",
            "topic",
            "ds_folder",
            "notifications",
            "followups_count",
            "comments_count",
            "site",
        ]
        read_only_fields = [
            "created_on",
            "updated_on",
            "created_by",
        ]

    contact = NestedContactSerializer(read_only=True)
    contact_id = serializers.IntegerField(write_only=True, required=False)

    resource = ResourceSerializer(read_only=True)
    resource_id = serializers.IntegerField(required=False)

    created_by = UserSerializer(read_only=True)
    document = DocumentSerializer(read_only=True, many=True)
    topic = TopicSerializer(read_only=True)
    ds_folder = DSFolderSerializer(read_only=True)

    notifications = serializers.SerializerMethodField()
    followups_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    site = serializers.SerializerMethodField()

    # FIXME : We should not send all the tasks to non switchtender users (filter
    # queryset on current_user)

    def get_site(self, obj: Task) -> dict[str, Any]:
        return {"name": obj.site.name, "id": obj.site.id}

    def get_notifications(self, obj: Task) -> dict[str, Any]:
        followup_ct = ContentType.objects.get_for_model(TaskFollowup)
        followup_ids = [followup.id for followup in obj.followups.all()]

        unread_notifications = (
            notifications_models.Notification.on_site.filter(
                recipient=self.current_user
            )
            .filter(
                action_object_content_type=followup_ct.pk,
                action_object_object_id__in=followup_ids,
            )
            .unread()
        )

        return {
            "count": unread_notifications.count(),
        }

    def get_followups_count(self, obj: Task) -> int:
        if hasattr(obj, "followups_count"):
            return obj.followups_count
        return obj.followups.count()

    def get_comments_count(self, obj: Task) -> int:
        if hasattr(obj, "commented_followups_count"):
            return obj.commented_followups_count
        return obj.followups.exclude(comment="").count()

    def create(self, validated_data):
        return super().create(
            validated_data
            | {
                "site": self.current_site,
                "created_by": self.current_user,
            }
        )

    def validate_contact_id(self, value: int) -> int:
        if not Contact.objects.filter(site=self.current_site, id=value).exists():
            raise serializers.ValidationError(
                f"Invalid contact ID {value} for site {self.current_site}."
            )
        return value

    def validate_resource_id(self, value: int) -> int:
        if not Resource.objects.filter(sites=self.current_site, id=value).exists():
            raise serializers.ValidationError(
                f"Invalid resource ID {value} for site {self.current_site}."
            )
        return value


class TaskNotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notifications_models.Notification
        fields = ["id", "actor", "verb", "action_object", "timestamp"]

    actor = GenericRelatedField({auth_models.User: UserSerializer()})
    action_object = GenericRelatedField(
        {Task: TaskSerializer(), TaskFollowup: TaskFollowupSerializer()}
    )


class TaskWebhookSerializer(serializers.ModelSerializer):
    resource = ResourceWebhookSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "status",
            "resource",
            "project",
        )


# eof
