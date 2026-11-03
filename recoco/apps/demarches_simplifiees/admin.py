from django.contrib import admin, messages
from django.contrib.sites.models import Site
from django.db.models import JSONField, QuerySet
from django.http import HttpRequest
from django_json_widget.widgets import JSONEditorWidget

from .models import DSMapping, DSResource
from .services import load_ds_resource_schema


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
