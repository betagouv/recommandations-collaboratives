from django.contrib import admin

from . import models


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name"]
    ordering = ["name"]


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name"]
    list_display = ["first_name", "last_name", "email", "phone_no"]
