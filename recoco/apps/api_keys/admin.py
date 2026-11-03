from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin
from rest_framework_api_key.models import APIKey

from .models import ServiceAPIKey

admin.site.unregister(APIKey)


@admin.register(ServiceAPIKey)
class ServiceAPIKeyAdmin(APIKeyModelAdmin):
    list_display = (
        "prefix",
        "name",
        "user",
        "site",
        "created",
        "expiry_date",
        "_has_expired",
        "revoked",
    )
    list_filter = ("site", "revoked", "created")
    list_select_related = ("user", "site")
    search_fields = ("name", "prefix", "user__username", "user__email")
    raw_id_fields = ("user",)
