from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recoco.utils import has_perm

from . import models
from .importers import ResourceImporter
from .serializers import ResourceSerializer, ResourceURIImportSerializer

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
    API endpoint that allows resources to be listed or edited
    """

    def get_queryset(self):
        qs = models.Resource.on_site
        if not has_perm(self.request.user, "sites.manage_resources", self.request.site):
            qs = qs.filter(status__gt=models.Resource.TO_REVIEW)
        return (
            qs.with_ds_annotations()
            .select_related("created_by", "category")
            .prefetch_related("tags")
            .order_by("-created_on", "-updated_on")
        )

    serializer_class = ResourceSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsResourceManagerOrReadOnly,
    ]

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
            resource = models.Resource.on_site.filter(
                imported_from=resource_uri
            ).first()
            if resource:
                return Response(
                    ResourceSerializer(resource).data, status=status.HTTP_200_OK
                )

            # Try to fetch it since we don't have it
            ri = ResourceImporter()
            resource = ri.from_uri(resource_uri)
            resource.site_origin = request.site
            resource.save()
            resource.sites.add(request.site)

            return Response(
                ResourceSerializer(resource).data, status=status.HTTP_201_CREATED
            )

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


# eof
