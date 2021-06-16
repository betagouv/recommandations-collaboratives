from django.contrib import admin

# encoding: utf-8

"""
Admin for project application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 13:55:23 CEST
"""


from django.contrib import admin

from . import models


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["created_on"]
    list_display = ["created_on", "name", "location"]


@admin.register(models.Note)
class NoteAdmin(admin.ModelAdmin):
    search_fields = ["content", "tags"]
    list_filter = ["tags", "created_on"]
    list_display = ["created_on", "project_name", "tags"]

    def project_name(self):
        return self.project.name


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ["content", "tags"]
    list_filter = ["deadline", "tags"]
    list_display = ["created_on", "deadline", "project_name", "tags"]

    def project_name(self):
        return self.project.name


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    search_fields = ["description", "the_file"]
    list_filter = ["created_on"]
    list_display = ["created_on", "description", "the_file"]


# eof
