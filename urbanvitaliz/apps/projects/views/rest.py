# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

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
        return models.Project.objects.for_user(self.request.user).order_by(
            "-created_on", "-updated_on"
        )

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for project tasks
    """

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])

        user_projects = list(
            models.Project.objects.for_user(self.request.user).values_list(flat=True)
        )

        if project_id not in user_projects:
            raise PermissionDenied()

        return models.Task.objects.filter(project_id=project_id).order_by(
            "-created_on", "-updated_on"
        )

    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


# eof
