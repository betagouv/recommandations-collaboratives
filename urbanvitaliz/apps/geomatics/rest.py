# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from . import models
from .serializers import CommuneSerializer, DepartmentSerializer


########################################################################
# REST API
########################################################################
class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows departments to be viewed or edited.
    """

    def get_queryset(self):
        return models.Department.objects.all().order_by("name")

    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommuneViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Commune to be viewed or edited.
    """

    def get_queryset(self):
        return models.Commune.objects.all().order_by("name")

    serializer_class = CommuneSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["postal"]


# eof
