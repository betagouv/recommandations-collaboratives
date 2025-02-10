from typing import Any

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import F, FloatField, Value
from django.db.models.functions import Coalesce, Round
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.settings import api_settings
from watson import search as watson_search


class TagsFilterbackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)

        tags = request.query_params.get("tags", None)
        if tags:
            tags = tags.split(",")
            queryset = queryset.filter(tags__name__in=tags)

        return queryset


class BaseSearchFilter(SearchFilter):
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

    def get_search_fields(
        self, view, request
    ) -> list[str | tuple[str, dict[str, Any]]]:
        """
        Search fields are obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the search fields based on request content.
        """
        return getattr(view, "search_fields", None)

    def get_search_min_rank(self, view, request) -> float:
        return getattr(view, "search_min_rank", 0.0)


class VectorSearchFilter(BaseSearchFilter):
    """
    Search filter that uses the Postgres full-text search vector to rank results.
    """

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        search_fields = self.get_search_fields(view, request)

        if not search_terms or not len(search_terms):
            return queryset.annotate(
                search_rank=Value(0.0, output_field=FloatField()),
            )

        search_vector = None
        for search_field in search_fields:
            if isinstance(search_field, tuple):
                _vector = SearchVector(search_field[0], **search_field[1])
            else:
                _vector = SearchVector(search_field, config="french")
            if search_vector is None:
                search_vector = _vector
            else:
                search_vector += _vector

        search_query = SearchQuery(search_terms, config="french")

        return (
            queryset.annotate(rank=SearchRank(search_vector, search_query))
            .filter(rank__gte=self.get_search_min_rank(view, request))
            .annotate(search_rank=Round(Coalesce(F("rank"), 0.0), precision=2))
            .order_by("-search_rank")
        )


class WatsonSearchFilter(BaseSearchFilter):
    """
    Search filter that uses the Watson search engine to filter results.
    """

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)

        if not search_terms or not len(search_terms):
            return queryset.annotate(search_rank=Value(0.0, output_field=FloatField()))

        search_min_rank = self.get_search_min_rank(view, request)
        search_text = " ".join(search_terms)

        return (
            watson_search.filter(queryset, search_text=search_text)
            .annotate(search_rank=F("watson_rank"))
            .filter(search_rank__gte=search_min_rank)
        )
