# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from copy import copy
from django.http import Http404
from django.db.models import Count, Q
from django.contrib.contenttypes.models import ContentType
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import models, signals
from ..serializers import (
    ProjectSerializer,
    TaskFollowupSerializer,
    TaskNotificationSerializer,
    TaskSerializer,
    UserProjectStatusSerializer,
    UserProjectStatusForListSerializer,
)


########################################################################
# REST API
########################################################################


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """

    def get_queryset(self):
        # TODO tune query set to prevent loads of requests on subqueries
        return self.queryset.for_user(self.request.user).order_by(
            "-created_on", "-updated_on"
        )

    queryset = models.Project.on_site
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskFollowupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for TaskFollowups
    """

    serializer_class = TaskFollowupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        task_id = int(self.kwargs["task_id"])

        user_projects = list(
            models.Project.on_site.for_user(self.request.user).values_list(flat=True)
        )

        if project_id not in user_projects:
            project = models.Project.objects.get(pk=project_id)
            if not (
                self.request.method == "GET"
                and self.request.user.has_perm("projects.use_tasks", project)
            ):
                raise PermissionDenied()

        return models.TaskFollowup.objects.filter(task_id=task_id)

    def create(self, request, project_id, task_id):
        data = request.data
        data["task_id"] = task_id
        data["who_id"] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for project tasks
    """

    def perform_update(self, serializer):
        original_object = self.get_object()
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

        if not self.request.user.has_perm("projects.use_tasks", task.project):
            raise PermissionDenied()

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

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])

        project = models.Project.on_site.get(pk=project_id)

        if not (
            self.request.user.has_perm("projects.view_tasks", project)
            or self.request.user.has_perm("sites.list_projects", self.request.site)
        ):
            raise PermissionDenied()

        return self.queryset.filter(project_id=project_id).order_by(
            "-created_on", "-updated_on"
        )

    queryset = models.Task.on_site
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


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
        self.get_queryset().mark_all_as_read(request.user)
        return Response({}, status=status.HTTP_200_OK)

    serializer_class = TaskNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


########################################################################
# user project statuses
########################################################################


class UserProjectStatusDetail(APIView):
    """Retrieve or update a user project status"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return models.UserProjectStatus.objects.get(pk=pk)
        except models.UserProjectStatus.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        ups = self.get_object(pk)
        if ups.user != request.user:
            raise Http404
        context = {"request": request}
        serializer = UserProjectStatusSerializer(ups, context=context)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        ups = self.get_object(pk)
        if ups.user != request.user:
            raise Http404
        context = {"request": request, "view": self, "format": format}
        serializer = UserProjectStatusSerializer(
            ups, context=context, data=request.data
        )
        if serializer.is_valid():
            old = copy(ups)
            new = serializer.save()
            if new:
                signals.project_userprojectstatus_updated.send(
                    sender=self, old_one=old, new_one=new
                )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProjectStatusList(APIView):
    """List all user project status"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        ups = fetch_the_site_ups_for_user(request.site, request.user)
        context = {"request": request}

        serializer = UserProjectStatusForListSerializer(ups, context=context, many=True)
        return Response(serializer.data)


def fetch_the_site_ups_for_user(site, user):
    """Returns the complete ups tree with children"""
    project_statuses = models.UserProjectStatus.objects.filter(
        user=user, project__deleted=None
    )

    # get projects with missing user project status
    ids = list(project_statuses.values_list("project__id", flat=True))
    projects = models.Project.on_site.for_user(user).exclude(id__in=ids)

    # create missing user project status
    create_missing_ups(user, site, projects)

    # fetch all projects statuses
    project_statuses = list(project_statuses.prefetch_related("user__profile"))
    # fetch all requested projects and their annotations in a single query
    project_ids = [ps.project_id for ps in project_statuses]
    projects = {p.id: p for p in fetch_site_projects_with_ids(site, project_ids)}

    # update project statuses with the right project
    for ps in project_statuses:
        ps.project = projects[ps.project_id]

    return project_statuses


def create_missing_ups(user, site, projects):
    """Create user projects statuses for given projects"""
    new_statuses = [
        models.UserProjectStatus(user=user, site=site, project=p, status="NEW")
        for p in projects
    ]
    models.UserProjectStatus.objects.bulk_create(new_statuses)


def fetch_site_projects_with_ids(site, ids):
    """Return site projects with given ids including annotations."""
    return (
        models.Project.objects.filter(id__in=ids)
        .prefetch_related("commune")
        .prefetch_related("switchtenders")
        .annotate(
            recommendation_count=Count(
                "tasks",
                filter=Q(tasks__public=True, tasks__site=site),
            )
        )
        .annotate(
            public_message_count=Count(
                "notes",
                filter=Q(notes__public=True, notes__site=site),
            )
        )
        .annotate(
            private_message_count=Count(
                "notes",
                filter=Q(notes__public=False, notes__site=site),
            )
        )
    )


# eof
