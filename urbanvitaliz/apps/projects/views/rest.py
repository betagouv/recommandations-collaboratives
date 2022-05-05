# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .. import models
from ..serializers import ProjectSerializer, TaskSerializer


########################################################################
# REST API
########################################################################
class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """

    def get_queryset(self):
        return models.Project.on_site.for_user(self.request.user).order_by(
            "-created_on", "-updated_on"
        )

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for project tasks
    """

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

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])

        user_projects = list(
            models.Project.on_site.for_user(self.request.user).values_list(flat=True)
        )

        if project_id not in user_projects:
            raise PermissionDenied()

        return self.queryset.filter(project_id=project_id).order_by(
            "-created_on", "-updated_on"
        )

    queryset = models.Task.on_site.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


# eof
