from rest_framework import viewsets

from urbanvitaliz.utils import TrigramSimilaritySearchFilter

from . import models, serializers

########################################################################
# REST API
########################################################################


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows searching for organizations"""

    search_fields = ["name"]

    filter_backends = [TrigramSimilaritySearchFilter]

    serializer_class = serializers.OrganizationSerializer

    def get_queryset(self):
        """Return a list of all organizations."""
        return models.Organization.on_site.all()


# eof
