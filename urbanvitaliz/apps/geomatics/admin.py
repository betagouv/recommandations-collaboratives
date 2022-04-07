from django.contrib import admin

from . import models


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Commune)
class CommuneAdmin(admin.ModelAdmin):
    search_fields = ["name", "postal", "insee"]
    list_display = ["name", "postal", "insee"]
