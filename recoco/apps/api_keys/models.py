from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.db import models
from rest_framework_api_key.models import AbstractAPIKey, BaseAPIKeyManager


class ServiceAPIKeyManager(BaseAPIKeyManager):
    def get_usable_keys(self):
        return (
            super()
            .get_usable_keys()
            .filter(user__is_active=True)
            .select_related("user", "site")
        )


class ServiceAPIKey(AbstractAPIKey):
    objects = ServiceAPIKeyManager()

    user = models.ForeignKey(
        auth_models.User,
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name="compte de service",
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name="site",
    )

    class Meta(AbstractAPIKey.Meta):
        verbose_name = "clé d'API"
        verbose_name_plural = "clés d'API"

    def __str__(self):
        return f"<ServiceAPIKey: {self.prefix} ({self.user.username})>"
