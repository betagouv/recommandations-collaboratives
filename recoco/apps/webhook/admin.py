from django.contrib import admin
from django.contrib.admin import StackedInline
from django_webhook.admin import (
    WebhookAdmin as BaseWebhookAdmin,
)
from django_webhook.admin import (
    WebhookSecretInline as BaseWebhookSecretInline,
)
from django_webhook.models import Webhook

from .models import WebhookSite


class WebhookSiteInline(StackedInline):
    model = WebhookSite
    fields = ("site",)
    extra = 0
    max_num = 1


class WebhookSecretInline(BaseWebhookSecretInline):
    max_num = 1


class WebhookAdmin(BaseWebhookAdmin):
    list_display = (
        "uuid",
        "url",
        "active",
        "site",
    )
    inlines = [WebhookSecretInline, WebhookSiteInline]
    select_related = ("webhooksite",)

    list_filter = ("active", "webhooksite__site")

    @admin.display(empty_value="-")
    def site(self, obj):
        return obj.webhooksite.site


admin.site.unregister(Webhook)
admin.site.register(Webhook, WebhookAdmin)
