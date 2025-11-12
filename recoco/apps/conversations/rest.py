#!/usr/bin/env python


from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from recoco import verbs
from recoco.apps.projects import models as projects_models
from recoco.utils import has_perm_or_403

from ...rest_api.permissions import BaseConversationPermission
from . import signals
from .models import Message
from .serializers import ActivitySerializer, MessageSerializer, ParticipantSerializer


class MessagePermission(BaseConversationPermission):
    def has_object_permission(self, request, view, obj: Message):
        return request.method in SAFE_METHODS or obj.posted_by == request.user


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, MessagePermission]

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        return Message.objects.filter(project_id=project_id).annotate(
            unread=Count(
                "notifications",
                filter=Q(
                    notifications__unread=True,
                    notifications__recipient=self.request.user,
                ),
            )
        )

    def perform_destroy(self, instance):
        instance.soft_delete()

    def perform_create(self, serializer):
        instance = serializer.save(
            posted_by=self.request.user, project_id=self.kwargs["project_id"]
        )
        signals.message_posted.send(sender=self.perform_create, message=instance)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def mark_as_read(self, request, project_id, pk):
        """
        Mark user's notifications as read for a given message.
        We do not need more than IsAuthenticated to ensure no side effects.
        XXX This exposes potential Message IDs from an unhautorized account (not critical)
        """

        is_hijacked = getattr(request.user, "is_hijacked", False)

        if not is_hijacked:
            message = self.get_object()

            message.notifications.unread().filter(
                public=True,
            ).mark_all_as_read(self.request.user)

        return Response(status=status.HTTP_202_ACCEPTED)


class ActivityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Permissions:
     - list/read, one/read for anyone having "projects.view_public_notes"
    """

    serializer_class = ActivitySerializer

    activity_verbs = [
        verbs.Recommendation.IN_PROGRESS,
        verbs.Recommendation.NOT_APPLICABLE,
        verbs.Recommendation.DONE,
    ]

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        project = projects_models.Project.objects.get(id=project_id)
        has_perm_or_403(self.request.user, "projects.view_public_notes", project)

        return project.target_actions.filter(verb__in=self.activity_verbs, public=True)


class ParticipantViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Permissions:
     - list/read, one/read for anyone having "projects.view_public_notes"
    """

    queryset = User.objects
    serializer_class = ParticipantSerializer

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        project = projects_models.Project.objects.get(id=project_id)
        has_perm_or_403(self.request.user, "projects.view_public_notes", project)

        return (
            self.queryset.prefetch_related("project_messages")
            .select_related("profile")
            .filter(project_messages__project=project)
            .distinct()
        )
