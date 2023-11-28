from django.contrib import admin, messages
from django.utils import timezone
from urbanvitaliz.apps.communication import digests

from . import models


@admin.register(models.Reminder)
class ReminderAdmin(admin.ModelAdmin):
    readonly_fields = (
        "kind",
        "project",
        "site",
        "state",
        "origin",
    )
    search_fields = ["project__name", "project__commune__name"]
    list_filter = ["kind", "deadline", "sent_on", "site"]
    list_display = ["deadline", "project", "kind", "sent_on"]

    actions = ["send_reminder"]

    @admin.action(description="Envoyer le(s) rappel(s) via Brevo")
    def send_reminder(self, request, queryset):
        for reminder in queryset.filter(kind=models.Reminder.NEW_RECO):
            if digests.send_new_recommendations_reminders_digest_by_project(
                site=reminder.site, project=reminder.project, dry_run=False
            ):
                reminder.sent_on = timezone.now()
                reminder.save()
                self.message_user(
                    request,
                    f'Rappel "{models.Reminder.KIND_CHOICES[reminder.kind][1]}"'
                    f"(B) envoyé à { reminder.project.owner }.",
                    messages.SUCCESS,
                )

        for reminder in queryset.filter(kind=models.Reminder.WHATS_UP):
            if digests.send_whatsup_reminders_digest_by_project(
                site=reminder.site, project=reminder.project, dry_run=False
            ):
                reminder.sent_on = timezone.now()
                reminder.save()
                self.message_user(
                    request,
                    f'Rappel "{models.Reminder.KIND_CHOICES[reminder.kind][1]}"'
                    f"(C) envoyé à { reminder.project.owner }.",
                    messages.SUCCESS,
                )


# eof
