# encoding: utf-8

from django.contrib import admin

from . import models


@admin.register(models.Invite)
class InviteAdmin(admin.ModelAdmin):
    search_fields = ["project__name", "email", "id"]
    list_filter = ["role"]
    list_display = ["created_on", "email", "project", "role"]
    readonly_fields = ("created_on", "accepted_on")
    ordering = ["-created_on"]
