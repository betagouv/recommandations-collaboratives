from django.contrib import admin

# encoding: utf-8

"""
Admin for project application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-06-16 11:10:27 CEST
"""


from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name", "icon"]
    list_filter = []
    list_display = ["name", "icon", "color"]


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    search_fields = ["title", "content"]
    list_filter = ["created_on"]
    list_display = ["created_on", "title"]


# eof
