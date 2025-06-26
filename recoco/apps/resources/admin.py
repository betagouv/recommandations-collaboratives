# encoding: utf-8

"""
Admin for resources application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-06-16 11:10:27 CEST
"""

from csvexport.actions import csvexport
from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin

from . import models


@admin.register(models.Category)
class CategoryAdmin(CompareVersionAdmin):
    search_fields = ["name", "icon"]
    list_filter = ["sites"]
    list_display = ["name", "icon", "color"]


@admin.register(models.Resource)
class ResourceAdmin(CompareVersionAdmin):
    actions = [csvexport]
    search_fields = ["title", "content"]
    list_filter = ["sites", "status", "updated_on"]
    list_display = ["title", "status", "category", "updated_on"]
    list_select_related = ("category",)


@admin.register(models.Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    search_fields = ["resource__title", "comments"]
    list_filter = ["site"]
    list_display = ["resource", "created_by"]


@admin.register(models.ResourceAddon)
class ResourceAddonAdmin(admin.ModelAdmin):
    list_display = (
        "recommendation",
        "nature",
        "enabled",
    )
    list_filter = ("nature",)


# eof
