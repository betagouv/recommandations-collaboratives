from django.contrib import admin

from . import models


@admin.register(models.Reminder)
class ReminderAdmin(admin.ModelAdmin):
    readonly_fields = (
        "deadline",
        "kind",
        "sent_on",
        "project",
        "site",
        "state",
        "origin",
    )
    search_fields = ["project__name", "project__commune__name"]
    list_filter = ["kind", "deadline", "sent_on", "site"]
    list_display = ["deadline", "project", "kind", "sent_on"]


# eof
