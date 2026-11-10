from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
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
        limit_choices_to={"profile__is_bot": True},
        help_text="Seuls les comptes marqués comme bot peuvent recevoir une clé",
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

    def clean(self):
        super().clean()
        self._check_user_is_bot()

    def save(self, *args, **kwargs):
        # also enforced outside of forms (e.g. objects.create_key())
        self._check_user_is_bot()
        super().save(*args, **kwargs)

    def _check_user_is_bot(self):
        if self.user_id is None:
            return
        if not auth_models.User.objects.filter(
            pk=self.user_id, profile__is_bot=True
        ).exists():
            raise ValidationError(
                {"user": "Une clé d'API ne peut être attribuée qu'à un compte bot."}
            )

    def __str__(self):
        return f"<ServiceAPIKey: {self.prefix} ({self.user.username})>"
