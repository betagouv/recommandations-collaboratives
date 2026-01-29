from rest_framework.filters import BaseFilterBackend


class ResourceCategoryFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        category = request.GET.get("category", None)
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset


class ResourceStatusFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        statuses = request.GET.getlist("status", None)
        if statuses:
            queryset = queryset.filter(status__in=statuses)
        return queryset
