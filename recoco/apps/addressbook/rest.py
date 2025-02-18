from rest_framework.filters import BaseFilterBackend
from rest_framework.viewsets import ModelViewSet
from waffle import switch_is_active

from recoco.rest_api.filters import VectorSearchFilter, WatsonSearchFilter
from recoco.rest_api.pagination import StandardResultsSetPagination
from recoco.rest_api.permissions import (
    IsStaffForSiteOrISAuthenticatedReadOnly,
    IsStaffForSiteOrReadOnly,
)

from . import serializers
from .models import Contact, Organization, OrganizationGroup


class OrganizationGroupViewSet(ModelViewSet):
    serializer_class = serializers.OrganizationGroupSerializer
    queryset = OrganizationGroup.objects.all()
    permission_classes = [IsStaffForSiteOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [VectorSearchFilter]
    search_fields = ["name"]
    search_min_rank = 0.05


class OrganizationViewSet(ModelViewSet):
    permission_classes = [IsStaffForSiteOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [VectorSearchFilter]
    search_fields = ["name"]
    search_min_rank = 0.05

    def get_queryset(self):
        return Organization.on_site.with_contacts_only().prefetch_related(
            "departments__region"
        )

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
        return queryset.filter(organization__name__istartswith=orga_sw)


class ContactViewSet(ModelViewSet):
    permission_classes = [IsStaffForSiteOrISAuthenticatedReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [OrgaStartswithFilterBackend]

    search_fields = [
        (
            "last_name",
            {"config": "french", "weight": "A"},
        ),
        (
            "first_name",
            {"config": "french", "weight": "A"},
        ),
        (
            "email",
            {"config": "french", "weight": "A"},
        ),
        (
            "division",
            {"config": "french", "weight": "B"},
        ),
        (
            "organization__name",
            {"config": "french", "weight": "B"},
        ),
        (
            "organization__group__name",
            {"config": "french", "weight": "B"},
        ),
        (
            "organization__departments__name",
            {"config": "french", "weight": "C"},
        ),
        (
            "organization__departments__code",
            {"weight": "C"},
        ),
        (
            "organization__departments__region__name",
            {"config": "french", "weight": "C"},
        ),
        (
            "organization__departments__region__code",
            {"weight": "C"},
        ),
    ]
    search_min_rank = 0.05

    def get_queryset(self):
        return Contact.on_site.all()

    def filter_queryset(self, queryset):
        backends = list(self.filter_backends)

        if switch_is_active("addressbook_contact_use_watson_search"):
            backends.append(WatsonSearchFilter)
        else:
            backends.append(VectorSearchFilter)

        for backend in backends:
            queryset = backend().filter_queryset(self.request, queryset, self)

        return queryset.distinct()

    def get_serializer_class(self):
        match self.action:
            case "list":
                return serializers.ContactListSerializer
            case "retrieve":
                return serializers.ContactDetailSerializer
            case _:
                return serializers.ContactSerializer
