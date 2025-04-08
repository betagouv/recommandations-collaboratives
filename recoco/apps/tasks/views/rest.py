# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recoco.apps.projects import models as projects_models
from recoco.apps.projects.utils import is_member
from recoco.utils import has_perm, has_perm_or_403

from .. import models, signals
from ..serializers import (
    TaskFollowupCreateSerializer,
    TaskFollowupSerializer,
    TaskNotificationSerializer,
    TaskSerializer,
)

logger = logging.getLogger(__name__)

########################################################################
# Task
########################################################################


class IsTaskViewerOrManagerToWrite(permissions.BasePermission):
    """
    Custom permission to check if user can view tasks on given project
    """

    def has_permission(self, request, view):
        project_id = int(view.kwargs.get("project_id"))
        project = projects_models.Project.on_site.get(pk=project_id)

        if request.method in permissions.SAFE_METHODS:
            return request.user.has_perm(
                "projects.view_tasks", project
            ) or request.user.has_perm("sites.list_projects", request.site)

        return request.user.has_perm("projects.use_tasks", project)


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for project tasks
    """

    queryset = models.Task.objects
    permission_classes = [permissions.IsAuthenticated, IsTaskViewerOrManagerToWrite]
    serializer_class = TaskSerializer

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        return (
            self.queryset.filter(project_id=project_id)
            .annotate(
                followups_count=Count("followups"),
                commented_followups_count=Count(
                    "followups", filter=~Q(followups__comment="")
                ),
            )
            .select_related(
                "ds_folder", "topic", "created_by__profile", "site", "project"
            )
            .prefetch_related("followups")
            .order_by("-created_on", "-updated_on")
        )

    def perform_create(self, serializer: TaskSerializer):
        project_id = int(self.kwargs["project_id"])
        project = projects_models.Project.on_site.get(pk=project_id)

        has_perm_or_403(self.request.user, "projects.manage_tasks", project)

        serializer.save(project=project)

    def perform_update(self, serializer: TaskSerializer):
        original_object = self.get_object()

        has_perm_or_403(
            self.request.user, "projects.manage_tasks", original_object.project
        )

        updated_object = serializer.save()

        if original_object.public is False and updated_object.public is True:
            signals.action_created.send(
                sender=self,
                task=updated_object,
                project=updated_object.project,
                user=self.request.user,
            )

    @action(
        methods=["post"],
        detail=True,
    )
    def move(self, request, project_id, pk):
        task = self.get_object()

        # Insert at top of bottom
        top = request.POST.get("top", None)
        bottom = request.POST.get("bottom", None)

        if top:
            task.top()
            return Response({"status": "insert top done"})

        if bottom:
            task.bottom()
            return Response({"status": "insert bottom done"})

        # Insert after or before another object
        above_id = request.POST.get("above", None)
        below_id = request.POST.get("below", None)

        if above_id:
            other_pk = above_id
        else:
            other_pk = below_id

        try:
            other_task = self.queryset.get(project_id=task.project_id, pk=other_pk)
        except models.Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if above_id:
            task.above(other_task)
            return Response({"status": "insert above done"})

        if below_id:
            task.below(other_task)
            return Response({"status": "insert below done"})

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["post"],
        detail=True,
    )
    def mark_visited(self, request, project_id, pk):
        task = self.get_object()

        has_perm_or_403(self.request.user, "projects.use_tasks", task.project)

        if not task.public:
            return Response(status=status.HTTP_403_FORBIDDEN)

        is_hijacked = getattr(request.user, "is_hijacked", False)

        if (not is_hijacked) and is_member(
            request.user, task.project, allow_draft=False
        ):
            task.visited = True
            task.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_304_NOT_MODIFIED)


########################################################################
# Task notification
########################################################################


class TaskNotificationViewSet(
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint for Task
    """

    def get_queryset(self):
        notifications = self.request.user.notifications.unread()

        task_id = self.kwargs["task_id"]

        try:
            task_id = int(self.kwargs["task_id"])
        except ValueError:
            logger.error(f"Task ID {task_id} should be an integer")
            return notifications.none()

        try:
            task = models.Task.objects.get(pk=task_id)
        except models.Task.DoesNotExist:
            logger.error(f"Task {task_id} does not exist")
            return notifications.none()

        task_ct = ContentType.objects.get_for_model(models.Task)
        followup_ct = ContentType.objects.get_for_model(models.TaskFollowup)

        task_actions = notifications.filter(
            action_object_content_type=task_ct.pk,
            action_object_object_id=task_id,
        )

        followup_ids = list(task.followups.all().values_list("id", flat=True))

        # FIXME cannot find who create notifications on followups
        followup_actions = notifications.filter(
            action_object_content_type=followup_ct.pk,
            action_object_object_id__in=followup_ids,
        )

        return task_actions | followup_actions

    @action(
        methods=["post"],
        detail=False,
    )
    def mark_all_as_read(self, request, project_id, task_id):
        is_hijacked = getattr(request.user, "is_hijacked", False)

        if not is_hijacked:
            self.get_queryset().mark_all_as_read(request.user)

        return Response({}, status=status.HTTP_200_OK)

    serializer_class = TaskNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


########################################################################
# Task followup
########################################################################


class IsTaskUser(permissions.BasePermission):
    """
    Custom permission to check if user can use task on given project
    """

    def has_permission(self, request, view):
        project_id = view.kwargs.get("project_id")
        user_projects = list(
            projects_models.Project.on_site.for_user(request.user).values_list(
                flat=True
            )
        )
        if project_id in user_projects:
            return True

        project = projects_models.Project.on_site.get(pk=project_id)
        return has_perm(request.user, "projects.use_tasks", project)


class TaskFollowupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for TaskFollowups
    """

    permission_classes = [
        permissions.IsAuthenticated,
        IsTaskUser,
    ]

    @property
    def task_id(self) -> int:
        return int(self.kwargs["task_id"])

    @property
    def project_id(self) -> int:
        return int(self.kwargs["project_id"])

    def get_queryset(self):
        # also filter with project_id to ensure the given task and project are consistent
        return models.TaskFollowup.objects.filter(
            task_id=self.task_id, task__project_id=self.project_id
        )

    def get_serializer_context(self):
        return super().get_serializer_context() | {
            "task_id": self.task_id,
            "project_id": self.project_id,
        }

    def get_serializer_class(self):
        if self.action == "create":
            return TaskFollowupCreateSerializer
        return TaskFollowupSerializer


# eof
