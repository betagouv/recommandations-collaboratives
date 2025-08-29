from django.contrib import admin

from . import models


class MarkdownNodeInline(admin.TabularInline):
    model = models.MarkdownNode
    extra = 1


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    inlines = [MarkdownNodeInline]
    readonly_fields = ("created", "modified")

    list_display = ("project", "posted_by", "created")
