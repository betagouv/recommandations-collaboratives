from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count

from .models import Hit, HitCount


class ContentObjectCTFilter(admin.SimpleListFilter):
    title = "Content object CT"
    parameter_name = "content_object_ct"

    def lookups(self, request, model_admin):
        return [
            (ct, ct)
            for ct in ContentType.objects.filter(
                hitcount_set_for_content__isnull=False
            ).distinct()
        ]

    def queryset(self, request, queryset):
        if value := self.value():
            return queryset.filter(content_object_ct=value)
        return queryset


class ContextObjectCTFilter(admin.SimpleListFilter):
    title = "Context object CT"
    parameter_name = "content_object_ct"

    def lookups(self, request, model_admin):
        return [
            (ct, ct)
            for ct in ContentType.objects.filter(
                hitcount_set_for_context__isnull=False
            ).distinct()
        ]

    def queryset(self, request, queryset):
        if value := self.value():
            return queryset.filter(content_object_ct=value)
        return queryset


@admin.register(HitCount)
class HitCountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "hit_count",
        "site",
        "created",
    )
    list_filter = (
        "site",
        ContentObjectCTFilter,
        ContextObjectCTFilter,
        "created",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(hit_count=Count("hits"))

    @admin.display(description="Name")
    def name(self, obj):
        return str(obj)

    @admin.display(description="Number of Hits")
    def hit_count(self, obj):
        return obj.hit_count


@admin.register(Hit)
class HitAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "hitcount",
        "created",
    )
    list_filter = ("created",)
