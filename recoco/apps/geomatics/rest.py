# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from . import models
from .serializers import (
    CommuneSerializer,
    DepartmentSerializer,
    RegionSerializer,
)


########################################################################
# REST API
########################################################################
class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return models.Department.objects.all().select_related("region").order_by("name")

    serializer_class = DepartmentSerializer


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return models.Region.objects.prefetch_related("departments").order_by("name")

    serializer_class = RegionSerializer


class CommuneViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return models.Commune.objects.select_related(
            "department", "department__region"
        ).order_by("name")

    serializer_class = CommuneSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["postal"]


# eof
