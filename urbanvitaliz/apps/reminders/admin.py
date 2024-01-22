from django.contrib import admin, messages
from urbanvitaliz.apps.communication import digests
from django.contrib.contenttypes.admin import GenericTabularInline

from urbanvitaliz.apps.communication import models as communication_models
from . import models


class ReminderTransactionTabularInline(GenericTabularInline):
    model = communication_models.TransactionRecord
    ct_field = "related_ct"
    ct_fk_field = "related_id"

    readonly_fields = ("transaction_id", "label", "user", "faked", "sent_on", "site")
    extra = 0


@admin.register(models.Reminder)
class ReminderAdmin(admin.ModelAdmin):
    readonly_fields = ("kind", "project", "site", "state", "origin")
    search_fields = ["project__name", "project__commune__name"]
    list_filter = ["kind", "deadline", "sent_on", "site"]
    list_display = ["deadline", "project", "kind", "sent_on"]

    actions = ["send_reminder"]

    inlines = (ReminderTransactionTabularInline,)

    @admin.action(description="Envoyer le(s) rappel(s) via Brevo")
    def send_reminder(self, request, queryset):
        for reminder in queryset.filter(kind=models.Reminder.NEW_RECO):
            if digests.send_new_recommendations_reminders_digest_by_project(
                site=reminder.site, project=reminder.project, dry_run=False
            ):
                reminder.mark_as_sent(reminder.project.owner)
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
                reminder.mark_as_sent(reminder.project.owner)
                reminder.save()
                self.message_user(
                    request,
                    f'Rappel "{models.Reminder.KIND_CHOICES[reminder.kind][1]}"'
                    f"(C) envoyé à { reminder.project.owner }.",
                    messages.SUCCESS,
                )


# eof
