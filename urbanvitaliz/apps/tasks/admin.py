# encoding: utf-8

"""
Admin for tasks application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 13:55:23 CEST
"""


from csvexport.actions import csvexport
from django.contrib import admin
from django.db.models import Count, F, Q
from ordered_model.admin import OrderedInlineModelAdminMixin, OrderedTabularInline

from . import models


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ["content", "tags"]
    list_filter = ["site", "deadline", "tags"]
    list_display = ["created_on", "deadline", "project_name", "tags", "topic"]

    actions = [csvexport]

    def project_name(self, o):
        return o.project.name


@admin.register(models.TaskFollowup)
class TaskFollowupAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TaskFollowupRsvp)
class TaskFollowupRsvpAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TaskRecommendation)
class TaskRecommendationAdmin(admin.ModelAdmin):
    pass


# eof
