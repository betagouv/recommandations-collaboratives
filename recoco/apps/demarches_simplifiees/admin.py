from django import forms
from django.contrib import admin, messages
from django.db.models import JSONField, QuerySet
from django.http import HttpRequest
from django_json_widget.widgets import JSONEditorWidget

from .models import DSFolder, DSMappingField, DSResource
from .tasks import load_ds_resource_schema, update_or_create_ds_folder


class DSMappingFieldInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["field_label"].widget.attrs["readonly"] = True

    class Meta:
        model = DSMappingField
        fields = ("field_label", "project_lookup_key", "enabled")


class DSMappingFieldInline(admin.TabularInline):
    model = DSMappingField
    extra = 0
    ordering = ("enabled", "field_label")
    form = DSMappingFieldInlineForm
    can_delete = False

    def has_add_permission(self, request, obj) -> bool:
        return False


@admin.register(DSResource)
class DSResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "preremplir_url", "number")
    search_fields = ("name",)
    actions = ("load_schema_action",)
    inlines = (DSMappingFieldInline,)

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

    @admin.action(description="Mettre à jour le matching projet / démarche simplifiée")
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
