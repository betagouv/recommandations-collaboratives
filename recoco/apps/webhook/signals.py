from django_webhook.signals import SignalListener
from recoco.apps.projects.models import Project
from django_webhook.models import Webhook
from typing import Any


class WebhookSignalListener(SignalListener):
    def _site_ids(self, instance: Any) -> list[int]:
        if isinstance(instance, Project):
            return instance.sites.values_list("id", flat=True)
        return []

    def find_webhooks(self, topic: str, instance: Any):
        return Webhook.objects.filter(
            active=True,
            topics__name=topic,
            webhooksite__site__in=self._site_ids(instance),
        ).values_list("id", "uuid")

    def serialize(self, instance):
        # TODO: do serializing per object type
        if isinstance(instance, Project):
            pass

        return super().serialize(instance)
