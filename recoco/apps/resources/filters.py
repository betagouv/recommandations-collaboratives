from rest_framework.filters import BaseFilterBackend


class ResourceCategoryFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        categories = request.GET.getlist("category", None)
        if categories:
            queryset = queryset.filter(category_id__in=categories)
        return queryset


class ResourceStatusFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        statuses = request.GET.getlist("status", None)
        if statuses:
            queryset = queryset.filter(status__in=statuses)
        return queryset
