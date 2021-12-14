# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from rest_framework import permissions, viewsets

from .. import models
from ..serializers import ProjectSerializer


########################################################################
# REST API
########################################################################
class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    def get_queryset(self):
        return models.Project.objects.in_departments(
            self.request.user.profile.departments.all()
        ).order_by("-created_on", "-updated_on")

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


# eof
