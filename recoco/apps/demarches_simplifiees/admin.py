from django.contrib import admin, messages
from django.contrib.sites.models import Site
from django.db.models import JSONField, QuerySet
from django.http import HttpRequest
from django_json_widget.widgets import JSONEditorWidget

from .models import DSFolder, DSMapping, DSResource
from .tasks import load_ds_resource_schema, update_or_create_ds_folder


@admin.register(DSResource)
class DSResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "preremplir_url", "number")
    search_fields = ("name",)

    actions = ("load_schema_action",)

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }

    @admin.action(description="Charger le schéma publique de la démarche simplifiée")
    def load_schema_action(self, request: HttpRequest, queryset: QuerySet[DSResource]):
        for ds_resource in queryset:
            load_ds_resource_schema.delay(ds_resource.id)
            self.message_user(
                request,
                f"Tâche déclenchée pour la resource '{ds_resource.name}'.",
                messages.SUCCESS,
            )


@admin.register(DSFolder)
class DSFolderAdmin(admin.ModelAdmin):
    list_display = (
        "dossier_id",
        "project",
        "ds_resource",
        "recommendation",
    )

    list_filter = ("created",)

    search_fields = (
        "project",
        "ds_resource",
        "dossier_id",
    )

    readonly_fields = (
        "content_hash",
        "dossier_id",
        "dossier_number",
        "dossier_prefill_token",
        "dossier_url",
        "project",
        "recommendation",
        "state",
    )

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }

    actions = ("update_matching",)

    ordering = ("-created",)
    list_select_related = (
        "project",
        "ds_resource",
        "recommendation",
    )

    @admin.action(description="Mettre à jour le matching dossier / démarche simplifiée")
    def update_matching(self, request: HttpRequest, queryset: QuerySet[DSResource]):
        for ds_folder in queryset:
            if not ds_folder.recommendation_id:
                self.message_user(
                    request,
                    f"Le dossier '{ds_folder.dossier_id}' n'a pas de recommandation liée.",
                    messages.ERROR,
                )
                continue

            update_or_create_ds_folder.delay(ds_folder.recommendation_id)
            self.message_user(
                request,
                f"Tâche déclenchée pour le dossier '{ds_folder.dossier_id}'.",
                messages.SUCCESS,
            )


class DSMappingAdminSiteFilter(admin.SimpleListFilter):
    title = "site"
    parameter_name = "site"

    def lookups(self, request, model_admin):
        return [(site.id, site.name) for site in Site.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(site=self.value())
        return queryset


@admin.register(DSMapping)
class DSMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "ds_resource", "site", "enabled")
    list_filter = ("enabled", DSMappingAdminSiteFilter)

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }
