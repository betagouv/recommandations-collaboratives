from rest_framework import permissions, viewsets
from .serializers import ResourceSerializer
from . import models


########################################################################
# REST API
########################################################################
class ResourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows resources to be listed or edited
    """

    def get_queryset(self):
        return models.Resource.on_site.exclude(status=models.Resource.DRAFT).order_by(
            "-created_on", "-updated_on"
        )

    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# eof
