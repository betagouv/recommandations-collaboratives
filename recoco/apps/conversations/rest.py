#!/usr/bin/env python


from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import mixins, viewsets
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated

from recoco import verbs
from recoco.apps.projects import models as projects_models
from recoco.utils import has_perm, has_perm_or_403

from .models import Message
from .serializers import ActivitySerializer, MessageSerializer, ParticipantSerializer


class MessagePermission(BasePermission):
    """
    Should allow:
    - list/read, one/read for anyone having "projects.view_public_notes"
    - list/create for anyone having "projects.use_public_notes"
    - one/update for anyone having "projects.use_public_notes" and owning the object (posted_by)
    """

    def has_permission(self, request, view):
        project = projects_models.Project.objects.get(pk=view.kwargs["project_id"])
        if request.method in SAFE_METHODS:
            return has_perm(request.user, "projects.view_public_notes", project)
        return has_perm(request.user, "projects.use_public_notes", project)

    def has_object_permission(self, request, view, obj: Message):
        return request.method in SAFE_METHODS or obj.posted_by == request.user


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, MessagePermission]

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        return Message.objects.filter(project_id=project_id).annotate(
            unread=Count("notifications", filter=Q(notifications__unread=True))
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"project_id": int(self.kwargs["project_id"])})
        return context

    def perform_destroy(self, instance):
        instance.delete()


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
