# encoding: utf-8

"""
Admin for tasks application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 13:55:23 CEST
"""


from csvexport.actions import csvexport
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html

from recoco.apps.demarches_simplifiees.tasks import update_or_create_ds_folder

from . import models


@admin.action(description="Mettre à jour ou créer un dossier DS")
def trigger_ds_folder_task(modeladmin, request, queryset):
    for task in queryset:
        update_or_create_ds_folder.delay(recommendation_id=task.id)
        modeladmin.message_user(
            request,
            f"Le dossier DS pour la tâche {task.id} va être mis à jour ou créé",
            messages.SUCCESS,
        )


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ["content", "tags"]
    list_filter = ["site", "deadline", "tags"]
    list_display = [
        "created_on",
        "deadline",
        "project_name",
        "tags",
        "topic",
        "ds_folder_link",
    ]
    readonly_fields = ["created_by", "project"]

    list_select_related = ("project", "ds_folder")

    actions = [
        csvexport,
        trigger_ds_folder_task,
    ]

    def project_name(self, o):
        return o.project.name

    @admin.display(description="Dossier pré-rempli DS")
    def ds_folder_link(self, obj):
        if obj.ds_folder:
            ds_folder_url = reverse(
                "admin:demarches_simplifiees_dsfolder_change", args=[obj.ds_folder.id]
            )
            return format_html(
                f'<a href="{ds_folder_url}">{obj.ds_folder.dossier_id}</a>'
            )


@admin.register(models.TaskFollowup)
class TaskFollowupAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TaskFollowupRsvp)
class TaskFollowupRsvpAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TaskRecommendation)
class TaskRecommendationAdmin(admin.ModelAdmin):
    list_select_related = ("resource",)


# eof
