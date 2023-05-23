from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from generic_relations.relations import GenericRelatedField
from notifications import models as notifications_models
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers
from urbanvitaliz.apps.geomatics.serializers import CommuneSerializer
from urbanvitaliz.apps.home.serializers import UserSerializer
from urbanvitaliz.apps.reminders import models as reminders_models
from urbanvitaliz.apps.reminders.serializers import ReminderSerializer

from .models import Document, Project, Task, TaskFollowup, UserProjectStatus, Note
from .utils import create_reminder, get_collaborators_for_project
from urbanvitaliz.utils import get_group_for_site


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "the_file",
            "the_link",
            "filename",
            "description",
            "uploaded_by",
            "created_on",
            "pinned",
        ]

    uploaded_by = UserSerializer(read_only=True, many=False)


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
            "is_observer",
            "commune",
            "notifications",
            "recommendation_count",
            "public_message_count",
            "private_message_count",
        ]

    switchtenders = UserSerializer(read_only=True, many=True)
    is_switchtender = serializers.SerializerMethodField()

    def get_is_switchtender(self, obj):
        request = self.context.get("request")
        return request.user in obj.switchtenders.all()

    is_observer = serializers.SerializerMethodField()

    def get_is_observer(self, obj):
        request = self.context.get("request")
        return request.user.pk in obj.switchtenders_on_site.filter(
            is_observer=True
        ).values_list("switchtender__id", flat=True)

    recommendation_count = serializers.SerializerMethodField()

    def get_recommendation_count(self, obj):
        return Task.on_site.published().filter(project=obj).count()

    public_message_count = serializers.SerializerMethodField()

    def get_public_message_count(self, obj):
        return Note.on_site.public().filter(project=obj).count()

    private_message_count = serializers.SerializerMethodField()

    def get_private_message_count(self, obj):
        return Note.on_site.private().filter(project=obj).count()

    commune = CommuneSerializer(read_only=True)

    notifications = serializers.SerializerMethodField()

    def get_notifications(self, obj):
        request = self.context.get("request")

        notifications = notifications_models.Notification.on_site.filter(
            recipient=request.user
        )

        project_ct = ContentType.objects.get_for_model(obj)

        advisor_group = get_group_for_site("advisor", request.site)
        advisors = [
            int(advisor)
            for advisor in advisor_group.user_set.values_list("id", flat=True)
        ]

        unread_notifications = notifications.filter(
            target_content_type=project_ct.pk, target_object_id=obj.pk
        ).unread()

        unread_public_messages = unread_notifications.filter(verb="a envoyé un message")
        unread_private_messages = unread_notifications.filter(
            verb="a envoyé un message dans l'espace conseillers"
        )
        new_recommendations = unread_notifications.filter(verb="a recommandé l'action")

        return {
            "count": unread_notifications.count(),
            "has_collaborator_activity": unread_notifications.exclude(
                actor_object_id__in=advisors
            ).exists(),
            "unread_public_messages": unread_public_messages.count(),
            "unread_private_messages": unread_private_messages.count(),
            "new_recommendations": new_recommendations.count(),
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
            if followup.who in get_collaborators_for_project(followup.task.project):
                create_reminder(
                    7 * 6, task, followup.who, origin=reminders_models.Reminder.SYSTEM
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
            "document",
            "reminders",
            "resource_id",
            "notifications",
            "followups_count",
            "comments_count",
        ]

    created_by = UserSerializer(read_only=True, many=False)
    reminders = ReminderSerializer(read_only=True, many=True)

    document = DocumentSerializer(read_only=True, many=True)

    notifications = serializers.SerializerMethodField()
    followups_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

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


class TaskNotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notifications_models.Notification
        fields = ["id", "actor", "verb", "action_object", "timestamp"]

    actor = GenericRelatedField({auth_models.User: UserSerializer()})
    action_object = GenericRelatedField(
        {Task: TaskSerializer(), TaskFollowup: TaskFollowupSerializer()}
    )


class UserProjectStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProjectStatus
        fields = ["id", "project", "status"]

    project = ProjectSerializer(read_only=True)


class UserProjectStatusForListSerializer(serializers.BaseSerializer):
    class Meta:
        model = UserProjectStatus
        fields = []

    def to_representation(self, data):
        """Return a representation of data (optimized version)"""
        # use our optimized queryset and not project serializer
        commune = data.project.commune
        commune_data = (
            {
                "name": commune.name,
                "insee": commune.insee,
                "postal": commune.postal,
                "department": {
                    "code": commune.department.code,
                    "name": commune.department.name,
                },
                "latitude": commune.latitude,
                "longitude": commune.longitude,
            }
            if commune
            else None
        )
        return {
            "id": data.id,
            "status": data.status,
            "project": {
                "id": data.project.id,
                "name": data.project.name,
                "org_name": data.project.org_name,
                "status": data.project.status,
                "created_on": data.project.created_on,
                "updated_on": data.project.updated_on,
                "switchtenders": [
                    {
                        "first_name": s.first_name,
                        "last_name": s.last_name,
                        "username": s.username,
                        "profile": {
                            "organization": {
                                "name": s.profile.organization.name
                                if s.profile.organization
                                else "",
                            }
                        },
                    }
                    for s in data.project.switchtenders.all()
                ],
                "is_switchtender": False,
                "is_observer": False,
                "commune": commune_data,
                "notifications": {
                    "count": 0,
                    "has_collaborator_activity": False,
                    "unread_public_messages": 0,
                    "unread_private_messages": 0,
                    "new_recommendations": 0,
                },
                "recommendation_count": data.project.recommendation_count,
                "public_message_count": data.project.public_message_count,
                "private_message_count": data.project.private_message_count,
            },
        }


# eof
