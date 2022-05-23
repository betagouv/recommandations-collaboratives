from django.contrib import admin

from . import models


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]
    ordering = ["name"]


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name", "organization__name"]
    list_display = ["last_name", "first_name", "email", "phone_no", "organization"]
    ordering = ["last_name", "first_name"]
