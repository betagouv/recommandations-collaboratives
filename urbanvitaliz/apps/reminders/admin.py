from django.contrib import admin

from . import models


@admin.register(models.Mail)
class MailAdmin(admin.ModelAdmin):
    search_fields = ["recipient", "subject"]
    list_filter = ["deadline", "sent_on"]
    list_display = ["recipient", "deadline", "sent_on"]


# eof
