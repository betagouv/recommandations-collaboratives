from django.contrib import admin

from .models import Hit, HitCount


@admin.register(HitCount)
class HitCountAdmin(admin.ModelAdmin):
    list_display = (
        "site",
        "content_object",
        "context_object",
        "created",
    )
    list_filter = (
        "site",
        "created",
    )


@admin.register(Hit)
class HitAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "hitcount",
        "created",
    )
    list_filter = ("created",)
