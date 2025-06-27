from django.contrib import admin
from reversion.admin import VersionAdmin

from . import models


@admin.register(models.OrganizationGroup)
class OrganizationGroupAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)
    ordering = ("name",)
    list_filter = (
        "created",
        "modified",
    )


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "group__name",
    )
    list_display = ("name",)
    ordering = ("name",)
    list_filter = (
        "sites",
        "group",
        "created",
        "modified",
    )
    list_select_related = ("group",)


@admin.register(models.Contact)
class ContactAdmin(VersionAdmin):
    search_fields = (
        "first_name",
        "last_name",
        "organization__name",
    )
    list_display = (
        "last_name",
        "first_name",
        "email",
        "phone_no",
        "organization",
    )
    ordering = ("last_name", "first_name")
    list_select_related = ("organization",)
