from typing import Any

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramBase,
    TrigramSimilarity,
    TrigramStrictWordSimilarity,
)
from django.db.models import Case, F, FloatField, Q, Value, When
from django.db.models.functions import Coalesce, Round
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.settings import api_settings
from watson import search as watson_search

from recoco.utils import strip_accents


class TagsFilterbackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)

        tags = request.query_params.get("tags", None)
        if tags:
            tags = tags.split(",")
            queryset = queryset.filter(tags__name__in=tags)

        return queryset


class BaseSearchFilter(SearchFilter):
    # Adapted from
    # https://medium.com/@dumanov/powerfull-and-simple-search-engine-in-django-rest-framework-cb24213f5ef5

    search_param = api_settings.SEARCH_PARAM
    template = "rest_framework/filters/search.html"
    search_title = _("Search")
    search_description = _("A search term.")

    view_search_fields = "search_fields"
    view_search_min_rank = "search_min_rank"

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

        return getattr(view, self.view_search_fields, None)

    def get_search_min_rank(self, view, request) -> float:
        return getattr(view, self.view_search_min_rank, 0.0)


class VectorSearchFilter(BaseSearchFilter):
    """Search filter that uses the Postgres full-text search vector to rank results."""

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
                _vector = SearchVector(
                    search_field[0],
                    **{"config": "french_unaccent", **search_field[1]},
                )
            else:
                _vector = SearchVector(
                    search_field,
                    config="french_unaccent",
                )

            if search_vector is None:
                search_vector = _vector
            else:
                search_vector += _vector

        search_query = SearchQuery(search_terms, config="french_unaccent")

        return (
            queryset.annotate(rank=SearchRank(search_vector, search_query))
            .filter(rank__gte=self.get_search_min_rank(view, request))
            .annotate(search_rank=Round(Coalesce(F("rank"), 0.0), precision=2))
            .order_by("-search_rank")
        )


class TrigramSimilaritySearchFilter(BaseSearchFilter):
    """Search filter that uses the Postgres trigram similarity to rank results."""

    view_search_fields = "trgm_search_fields"
    view_search_min_rank = "trgm_search_min_rank"

    def get_similarity_trgm_obj(
        self, search_field: str, search_terms: str
    ) -> TrigramBase:
        return TrigramSimilarity(search_field, search_terms)

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        search_fields = self.get_search_fields(view, request)

        if not search_terms or not len(search_terms):
            return queryset.annotate(
                search_rank=Value(0.0, output_field=FloatField()),
            )

        search_terms = strip_accents(" ".join(search_terms))

        trgm_similarity_threshold = self.get_search_min_rank(view, request)

        search_filters = Q()
        search_rank_fields = None

        max_boost: float = max(
            1.0,
            *(
                search_field[1] if isinstance(search_field, tuple) else 1.0
                for search_field in search_fields
            ),
        )

        for search_field in search_fields:
            if isinstance(search_field, tuple):
                search_field_name = search_field[0]
                similarity_field = f"{search_field[0]}_trgm_similarity"
                boost = float(search_field[1]) / max_boost
            else:
                search_field_name = search_field
                similarity_field = f"{search_field}_trgm_similarity"
                boost = 1.0 / max_boost

            queryset = queryset.annotate(
                **{
                    similarity_field: self.get_similarity_trgm_obj(
                        search_field=f"{search_field_name}__unaccent",
                        search_terms=search_terms,
                    )
                }
            ).annotate(
                **{
                    f"{similarity_field}_rank": Case(
                        When(
                            **{f"{similarity_field}__gt": trgm_similarity_threshold},
                            then=Round(
                                Coalesce(F(similarity_field) * Value(boost), 0.0),
                                precision=2,
                            ),
                        ),
                        default=Value(0.0),
                    )
                }
            )

            search_filters |= Q(
                **{f"{similarity_field}__gt": trgm_similarity_threshold}
            )

            if search_rank_fields is None:
                search_rank_fields = F(f"{similarity_field}_rank")
            else:
                search_rank_fields += F(f"{similarity_field}_rank")

        return (
            queryset.filter(search_filters)
            .annotate(search_rank=search_rank_fields)
            .order_by("-search_rank")
        )


class StrictWordTrigramSimilaritySearchFilter(TrigramSimilaritySearchFilter):
    def get_similarity_trgm_obj(
        self, search_field: str, search_terms: str
    ) -> TrigramBase:
        return TrigramStrictWordSimilarity(search_terms, search_field)


class WatsonSearchFilter(BaseSearchFilter):
    """Search filter that uses the Watson search engine to filter results."""

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)

        if not search_terms or not len(search_terms):
            return queryset.annotate(search_rank=Value(0.0, output_field=FloatField()))

        search_min_rank = self.get_search_min_rank(view, request)
        search_text = strip_accents(" ".join(search_terms))

        return (
            watson_search.filter(queryset, search_text=search_text)
            .annotate(search_rank=F("watson_rank"))
            .filter(search_rank__gte=search_min_rank)
        )
