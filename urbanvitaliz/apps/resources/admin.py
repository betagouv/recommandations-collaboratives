# encoding: utf-8

"""
Admin for resources application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-06-16 11:10:27 CEST
"""


from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name", "icon"]
    list_filter = ["sites"]
    list_display = ["name", "icon", "color"]


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    search_fields = ["title", "content"]
    list_filter = ["sites", "updated_on"]
    list_display = ["title", "status", "category", "updated_on"]


@admin.register(models.Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    search_fields = ["resource__title", "comments"]
    list_filter = []
    list_display = ["resource", "created_by"]


# eof
