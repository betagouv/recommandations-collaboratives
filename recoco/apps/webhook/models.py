from django.db import models
from django.contrib.sites.models import Site
from django_webhook.models import Webhook


class WebhookSite(models.Model):
    webhook = models.OneToOneField(
        Webhook,
        on_delete=models.CASCADE,
        related_name="webhooksite",
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="webhooksites",
    )

    def __str__(self):
        return f"{self.site} - {str(self.webhook.uuid)}"

    class Meta:
        verbose_name = "Webhook Site"
        verbose_name_plural = "Webhook Sites"
        unique_together = ("webhook", "site")
