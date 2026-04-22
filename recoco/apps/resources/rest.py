import reversion
from django.db import transaction
from django.db.models import Count, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from reversion.models import Version

from recoco.rest_api.filters import WatsonSearchFilter
from recoco.rest_api.pagination import StandardResultsSetPagination
from recoco.utils import has_perm

from ..tasks.models import Task
from .filters import ResourceCategoryFilter, ResourceStatusFilter
from .importers import ResourceImporter
from .models import Resource, ResourceAddon, ResourceRevisionMeta
from .serializers import (
    ResourceAddonSerializer,
    ResourceDetailSerializer,
    ResourceSerializer,
    ResourceURIImportSerializer,
    ResourceWritableSerializer,
)

########################################################################
# REST API
########################################################################


class IsResourceManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to check if user can create or update resource on current site
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return has_perm(request.user, "sites.manage_resources", request.site)


class ResourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows resources to be listed or edited, with pagination support.
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsResourceManagerOrReadOnly,
    ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        WatsonSearchFilter,
        ResourceCategoryFilter,
        ResourceStatusFilter,
    ]

    def get_queryset(self):
        qs = Resource.on_site
        if not has_perm(self.request.user, "sites.manage_resources", self.request.site):
            qs = qs.filter(status__gt=Resource.TO_REVIEW)

        task_sb = (
            Task.objects.filter(
                project__exclude_stats=False,
                site_id=self.request.site,
                resource_id=OuterRef("pk"),
            )
            .order_by()
            .values("resource")
            .annotate(c=Count("*"))
            .values_list("c", flat=True)
        )
        return (
            qs.with_ds_annotations()
            .select_related("created_by", "category")
            .prefetch_related("tags")
            .order_by("-created_on", "-updated_on")
            .annotate(nb_uses=Coalesce(Subquery(task_sb), Value(0)))
        )

    def get_permissions(self):
        # Any authenticated user can submit a patch proposal via PATCH/PUT with as_patch=True
        if self.action in ("update", "partial_update") and self.request.data.get(
            "as_patch", False
        ):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        match self.action:
            case "list":
                return ResourceSerializer
            case "retrieve":
                return ResourceDetailSerializer
            case "partial_update":
                return ResourceWritableSerializer
            case "update":
                return ResourceWritableSerializer
            case "create":
                return ResourceWritableSerializer
            case _:
                return ResourceSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.pop("as_patch", False):
            meta = self._create_patch_proposal(request, instance, serializer)
            return Response(
                {"id": meta.pk, "revision_id": meta.revision_id},
                status=status.HTTP_201_CREATED,
            )

        self.perform_update(serializer)
        return Response(serializer.data)

    def _create_patch_proposal(self, request, resource, serializer):
        """Apply proposed changes into a reversion revision, then revert the live object.
        Based on a discussion with django-reversion author:
        https://github.com/etianen/django-reversion/issues/727"""
        data = serializer.validated_data

        with transaction.atomic():
            current_versions = Version.objects.get_for_object(resource)
            current_version = current_versions.first()

            # Ensure there is a baseline version to revert to
            if not current_version:
                with reversion.create_revision():
                    resource.save()
                    reversion.set_comment("Baseline")
                current_version = Version.objects.get_for_object(resource).first()

            # Apply proposed fields and create the pending revision
            with reversion.create_revision():
                for field in (
                    "title",
                    "subtitle",
                    "summary",
                    "content",
                    "category",
                    "expires_on",
                ):
                    if field in data:
                        setattr(resource, field, data[field])
                resource.save()
                if "contacts" in data:
                    resource.contacts.set(data["contacts"])
                if "departments" in data:
                    resource.departments.set(data["departments"])
                reversion.set_user(request.user)
                reversion.set_comment("Proposition de modification")

            pending_version = Version.objects.get_for_object(resource).first()

            meta = ResourceRevisionMeta.objects.create(
                revision=pending_version.revision,
                resource=resource,
                proposed_by=request.user,
            )

            # Revert the live object to its state before the proposal
            current_version.revert()

        return meta

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def import_from_uri(self, request):
        """Import (create) a resource from an external known site, miroring it.

        FIXME The current permissions do not allow a fine grained access, thus it is
        left open to authenticated users. It should be restricted to only advisors or
        invited advisors.

        """
        serializer = ResourceURIImportSerializer(data=request.data)
        if serializer.is_valid():
            resource_uri = serializer.validated_data["uri"]

            # Check if we already have this resource
            resource = Resource.on_site.filter(imported_from=resource_uri).first()
            if resource:
                return Response(
                    ResourceDetailSerializer(resource).data, status=status.HTTP_200_OK
                )

            # Try to fetch it since we don't have it
            ri = ResourceImporter()
            resource = ri.from_uri(resource_uri)
            resource.site_origin = request.site
            resource.save()
            resource.sites.add(request.site)

            return Response(
                ResourceDetailSerializer(resource).data, status=status.HTTP_201_CREATED
            )

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class IsResourceManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return has_perm(request.user, "sites.manage_resources", request.site)


class ResourceAddonViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        IsResourceManager,
    ]
    serializer_class = ResourceAddonSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["recommendation", "nature"]

    def get_queryset(self):
        return ResourceAddon.objects.filter(recommendation__site=self.request.site)


# eof
