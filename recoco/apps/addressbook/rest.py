from rest_framework.viewsets import ModelViewSet

from recoco.rest_api.filters import SearchVectorFilter
from recoco.rest_api.pagination import StandardResultsSetPagination
from recoco.rest_api.permissions import (
    IsStaffOrISAuthenticatedReadOnly,
    IsStaffOrReadOnly,
)

from .models import Contact, Organization, OrganizationGroup
from .serializers import (
    ContactCreateSerializer,
    ContactSerializer,
    OrganizationGroupSerializer,
    OrganizationSerializer,
)


class OrganizationGroupViewSet(ModelViewSet):
    serializer_class = OrganizationGroupSerializer
    queryset = OrganizationGroup.objects.all()
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardResultsSetPagination
    search_fields = ["name"]
    filter_backends = [SearchVectorFilter]


class OrganizationViewSet(ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.on_site.all()
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = StandardResultsSetPagination
    search_fields = ["name"]
    filter_backends = [SearchVectorFilter]

    def get_queryset(self):
        return super().get_queryset().prefetch_related("departments__region")


class ContactViewSet(ModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.on_site.all()
    permission_classes = [IsStaffOrISAuthenticatedReadOnly]
    pagination_class = StandardResultsSetPagination
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
    search_min_rank = 0.2
    filter_backends = [SearchVectorFilter]

    def get_serializer_class(self):
        return ContactCreateSerializer if self.action == "create" else ContactSerializer
