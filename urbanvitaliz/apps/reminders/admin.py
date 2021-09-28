from django.contrib import admin

from . import models


@admin.register(models.Mail)
class MailAdmin(admin.ModelAdmin):
    search_fields = ["recipient", "subject"]
    list_filter = ["deadline", "sent"]
    list_display = ["recipient", "deadline", "sent"]


# eof
