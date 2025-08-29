from django.contrib import admin

from . import models


class MarkdownNodeInline(admin.TabularInline):
    model = models.MarkdownNode
    extra = 1


class ContactNodeInline(admin.TabularInline):
    model = models.ContactNode
    extra = 1


class DocumentNodeInline(admin.TabularInline):
    model = models.DocumentNode
    extra = 1


class RecommendationNodeInline(admin.TabularInline):
    model = models.RecommendationNode
    extra = 1


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    inlines = [
        MarkdownNodeInline,
        ContactNodeInline,
        DocumentNodeInline,
        RecommendationNodeInline,
    ]
    readonly_fields = ("created", "modified")

    list_display = ("project", "posted_by", "created")
