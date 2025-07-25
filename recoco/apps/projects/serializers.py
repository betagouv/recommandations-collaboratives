from django.contrib.contenttypes.models import ContentType
from notifications import models as notifications_models
from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer

from recoco import verbs
from recoco.apps.geomatics.serializers import CommuneSerializer
from recoco.apps.home.serializers import UserSerializer
from recoco.apps.tasks import models as task_models
from recoco.rest_api.serializers import BaseSerializerMixin
from recoco.utils import get_group_for_site

from .models import Document, Note, Project, ProjectSite, Topic, UserProjectStatus


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


class InlineProjectSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSite
        fields = ["id", "site", "is_origin", "status"]
        read_only_fields = ["id", "site", "is_origin"]


class ProjectSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSite
        fields = ["id", "project", "site", "is_origin", "status"]
        read_only_fields = ["id", "project", "site", "is_origin"]


class ProjectSerializer(
    TaggitSerializer, BaseSerializerMixin, serializers.HyperlinkedModelSerializer
):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "inactive_since",
            "status",
            "created_on",
            "updated_on",
            "org_name",
            "switchtenders",
            "commune",
            "location",
            "latitude",
            "longitude",
            "recommendation_count",
            "public_message_count",
            "private_message_count",
            "project_sites",
            "tags",
            "is_diagnostic_done",
            "advisors_note",
        ]

    switchtenders = UserSerializer(read_only=True, many=True)
    tags = TagListSerializerField()

    recommendation_count = serializers.SerializerMethodField()

    project_sites = InlineProjectSiteSerializer(read_only=True, many=True)

    def get_recommendation_count(self, obj):
        return task_models.Task.on_site.published().filter(project=obj).count()

    public_message_count = serializers.SerializerMethodField()

    def get_public_message_count(self, obj):
        return Note.on_site.public().filter(project=obj).count()

    private_message_count = serializers.SerializerMethodField()

    def get_private_message_count(self, obj):
        return Note.on_site.private().filter(project=obj).count()

    commune = CommuneSerializer(read_only=True)

    latitude = serializers.SerializerMethodField()

    def get_latitude(self, obj):
        return obj.location_y

    longitude = serializers.SerializerMethodField()

    def get_longitude(self, obj):
        return obj.location_x

    advisors_note = serializers.SerializerMethodField()

    def get_advisors_note(self, obj) -> str | None:
        if self.current_user and self.current_user.has_perm(
            "projects.use_private_notes", obj
        ):
            return obj.advisors_note


class UserProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + [
            "is_switchtender",
            "is_observer",
            "notifications",
        ]

    is_switchtender = serializers.SerializerMethodField()

    def get_is_switchtender(self, obj):
        # FIXME check that we should reduce switchteders to current site
        request = self.context.get("request")
        return request.user in obj.switchtenders.all()

    is_observer = serializers.SerializerMethodField()

    def get_is_observer(self, obj):
        request = self.context.get("request")
        return request.user.pk in obj.switchtender_sites.on_site().filter(
            is_observer=True
        ).values_list("switchtender__id", flat=True)

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

        unread_public_messages = unread_notifications.filter(
            verb=verbs.Conversation.PUBLIC_MESSAGE
        )
        unread_private_messages = unread_notifications.filter(
            verb=verbs.Conversation.PRIVATE_MESSAGE
        )
        new_recommendations = unread_notifications.filter(
            verb=verbs.Recommendation.CREATED
        )

        return {
            "count": unread_notifications.count(),
            "has_collaborator_activity": unread_notifications.exclude(
                actor_object_id__in=advisors
            ).exists(),
            "unread_public_messages": unread_public_messages.count(),
            "unread_private_messages": unread_private_messages.count(),
            "new_recommendations": new_recommendations.count(),
        }


class ProjectForListSerializer(BaseSerializerMixin):
    class Meta:
        model = Project
        fields = []

    def to_representation(self, data):
        """Return a representation of data (optimized version)"""
        # uses our optimized queryset and not project serializer
        commune = data.commune
        commune_data = format_commune(commune)

        return {
            "id": data.id,
            "name": data.name,
            "description": data.description,
            "org_name": data.org_name,
            "status": data.project_site_status,
            "inactive_since": data.inactive_since,
            "created_on": data.created_on,
            "updated_on": data.updated_on,
            "switchtenders": format_switchtenders(data),
            "is_switchtender": data.is_switchtender,
            "is_observer": data.is_observer,
            "commune": commune_data,
            "location": data.location,
            "latitude": data.location_y,
            "longitude": data.location_x,
            "notifications": data.notifications,
            "project_sites": format_sites(data),
            "tags": [tag.name for tag in data.tags.all()],
            "advisors_note": (
                data.advisors_note
                if self.current_user
                and self.current_user.has_perm("projects.use_private_notes", data)
                else None
            ),
            "owner": format_owner(data),
        }


class UserProjectStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProjectStatus
        fields = ["id", "project", "status"]

    project = UserProjectSerializer(read_only=True)


class UserProjectStatusForListSerializer(serializers.BaseSerializer):
    class Meta:
        model = UserProjectStatus
        fields = []

    def to_representation(self, data):
        """Return a representation of data (optimized version)"""
        # use our optimized queryset and not project serializer
        commune_data = format_commune(data.project.commune)

        return {
            "id": data.id,
            "status": data.status,
            "project": {
                "id": data.project.id,
                "name": data.project.name,
                "org_name": data.project.org_name,
                "status": data.project.project_sites.current().status,
                "created_on": data.project.created_on,
                "updated_on": data.project.updated_on,
                "switchtenders": format_switchtenders(data.project),
                "inactive_since": data.project.inactive_since,
                "is_switchtender": data.is_switchtender,
                "is_observer": data.is_observer,
                "commune": commune_data,
                "notifications": data.project.notifications,
                "recommendation_count": data.project.recommendation_count,
                "public_message_count": data.project.public_message_count,
                "private_message_count": data.project.private_message_count,
                "project_sites": format_sites(data.project),
            },
        }


def format_owner(project):
    owner = project.owner
    if not owner:
        return None
    return {
        "id": owner.id,
        "first_name": owner.first_name,
        "last_name": owner.last_name,
        "username": owner.username,
        "email": owner.email,
        "profile": {
            "organization": {
                "name": (
                    owner.profile.organization.name
                    if owner.profile.organization
                    else ""
                ),
            }
        },
    }


def format_commune(commune):
    if not commune:
        return None
    return {
        "name": commune.name,
        "insee": commune.insee,
        "postal": commune.postal,
        "department": {
            "code": commune.department.code,
            "name": commune.department.name,
            "region": {
                "code": commune.department.region.code,
                "name": commune.department.region.name,
            },
        },
        "latitude": commune.latitude,
        "longitude": commune.longitude,
    }


def format_switchtenders(project):
    return [
        {
            "first_name": s.first_name,
            "last_name": s.last_name,
            "username": s.username,
            "email": s.email,
            "profile": {
                "organization": {
                    "name": (
                        s.profile.organization.name if s.profile.organization else ""
                    ),
                }
            },
        }
        for s in project.switchtenders.all()
    ]


def format_sites(project):
    return [
        {
            "id": ps.id,
            "site": ps.site_id,
            "is_origin": ps.is_origin,
            "status": ps.status,
        }
        for ps in project.project_sites.all()
    ]


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Topic

        fields = ["name"]


# eof
