from rest_framework.filters import SearchFilter
from rest_framework.settings import api_settings
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets

from . import models, serializers

########################################################################
# REST API
########################################################################


class TrigramSimilaritySearchFilter(SearchFilter):
    # Adapted from https://medium.com/@dumanov/powerfull-and-simple-search-engine-in-django-rest-framework-cb24213f5ef5
    search_param = api_settings.SEARCH_PARAM
    template = "rest_framework/filters/search.html"
    search_title = _("Search")
    search_description = _("A search term.")

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, "")
        params = params.replace("\x00", "")  # strip null characters
        params = params.replace(",", " ")
        return params.split()

    def get_search_fields(self, view, request):
        """
        Search fields are obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the search fields based on request content.
        """
        return getattr(view, "search_fields", None)

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        # if no search_terms return
        if not search_terms:
            return queryset.none()

        # make conditions
        conditions = {}
        for search_field in search_fields:
            conditions[f"{search_field}__trigram_similar"] = search_terms

        print(conditions)
        queryset = queryset.filter(**conditions)

        return queryset


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows searching for Orgs
    """

    search_fields = ["name"]

    filter_backends = [TrigramSimilaritySearchFilter]

    serializer_class = serializers.OrganizationSerializer

    def get_queryset(self):
        """
        Return a list of all users.
        """
        return models.Organization.on_site.all()
