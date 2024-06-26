from django.contrib import admin

from .models import DemarcheSimplifiee, DossierPreRempli


@admin.register(DemarcheSimplifiee)
class DemarcheSimplifieeAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "description",
        "ds_id",
    )
    search_fields = (
        "nom",
        "description",
    )


@admin.register(DossierPreRempli)
class DossierPreRempliAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "demarche",
        "dossier_id",
        "dossier_url",
        "dossier_number",
    )
    search_fields = (
        "project",
        "demarche",
        "dossier_id",
    )
