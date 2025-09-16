from rest_framework.filters import BaseFilterBackend
from rest_framework.viewsets import ModelViewSet

from recoco.rest_api.filters import (
    StrictWordTrigramSimilaritySearchFilter,
)
from recoco.rest_api.pagination import StandardResultsSetPagination
from recoco.rest_api.permissions import (
    IsStaffForSiteOrIsAuthenticatedReadOnly,
    IsStaffForSiteOrReadOnly,
)

from . import serializers
from .models import Contact, Organization, OrganizationGroup


class OrganizationGroupViewSet(ModelViewSet):
    serializer_class = serializers.OrganizationGroupSerializer
    queryset = OrganizationGroup.objects.all()
    permission_classes = [IsStaffForSiteOrReadOnly]
    pagination_class = StandardResultsSetPagination

    filter_backends = [StrictWordTrigramSimilaritySearchFilter]

    trgm_search_fields = ["name"]
    trgm_search_min_rank = 0.3


class OrganizationViewSet(ModelViewSet):
    permission_classes = [IsStaffForSiteOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [StrictWordTrigramSimilaritySearchFilter]

    trgm_search_fields = [("name", 1.5), "group__name"]
    trgm_search_min_rank = 0.3

    search_fields = ["name"]
    search_min_rank = 0.05

    def get_queryset(self):
        return Organization.on_site.all().prefetch_related("departments__region")

    def get_serializer_class(self):
        match self.action:
            case "list":
                return serializers.OrganizationListSerializer
            case "retrieve":
                return serializers.OrganizationDetailSerializer
            case _:
                return serializers.OrganizationSerializer


class OrgaStartswithFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        orga_sw = request.query_params.get("orga-startswith")
        if not orga_sw:
            return queryset
        return queryset.filter(organization__name__istartswith=orga_sw).order_by(
            "organization__name", "last_name", "first_name"
        )


class ByDepartmentFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        departments_str = request.query_params.getlist("departments")
        departments = [int(dep_str) for dep_str in departments_str]
        if not departments:
            return queryset
        return queryset.filter(organization__departments__in=departments)


class ContactViewSet(ModelViewSet):
    filter_backends = [
        OrgaStartswithFilterBackend,
        ByDepartmentFilterBackend,
        StrictWordTrigramSimilaritySearchFilter,
    ]
    permission_classes = [IsStaffForSiteOrIsAuthenticatedReadOnly]
    pagination_class = StandardResultsSetPagination

    trgm_search_fields = [
        ("last_name", 1.25),
        "first_name",
        ("division", 1.25),
        ("organization__name", 1.5),
        "organization__group__name",
    ]
    trgm_search_min_rank = 0.37

    def get_queryset(self):
        return Contact.on_site.select_related("organization__group")

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).distinct()

    def get_serializer_class(self):
        match self.action:
            case "list":
                return serializers.ContactListSerializer
            case "retrieve":
                return serializers.ContactDetailSerializer
            case _:
                return serializers.ContactSerializer
