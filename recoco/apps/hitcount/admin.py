from django.contrib import admin
from django.db.models import Count

from .models import Hit, HitCount


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
