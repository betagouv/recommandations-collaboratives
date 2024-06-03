# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from copy import copy

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recoco.apps.projects import models as projects_models
from recoco.utils import has_perm, has_perm_or_403

from .. import models, signals
from ..serializers import (
    TaskFollowupSerializer,
    TaskNotificationSerializer,
    TaskSerializer,
)

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

    queryset = models.Task.on_site
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskViewerOrManagerToWrite]

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        return self.queryset.filter(project_id=project_id).order_by(
            "-created_on", "-updated_on"
        )

    def perform_create(self, serializer: TaskSerializer):
        site = get_current_site(self.request)
        project_id = int(self.kwargs["project_id"])
        project = projects_models.Project.on_site.get(pk=project_id)

        has_perm_or_403(self.request.user, "projects.manage_tasks", project)

        serializer.save(created_by=self.request.user, site=site, project=project)

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
        task_id = int(self.kwargs["task_id"])
        task = models.Task.objects.get(pk=task_id)

        notifications = self.request.user.notifications.unread()

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

    serializer_class = TaskFollowupSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTaskUser,
    ]

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        task_id = int(self.kwargs["task_id"])

        # also filter with project_id to ensure the given task and project are consistent
        return models.TaskFollowup.objects.filter(
            task_id=task_id, task__site=self.request.site, task__project_id=project_id
        )

    def create(self, request, project_id, task_id):
        data = copy(request.data)
        data["task_id"] = task_id
        data["who_id"] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


# eof
