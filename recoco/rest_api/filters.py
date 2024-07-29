from django_filters.rest_framework import DjangoFilterBackend


class TagsFilterbackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)

        tags = request.query_params.get("tags", None)
        if tags:
            tags = tags.split(",")
            queryset = queryset.filter(tags__name__in=tags)

        return queryset
