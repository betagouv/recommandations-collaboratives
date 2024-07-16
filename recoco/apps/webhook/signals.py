from typing import Any

from django_webhook.models import Webhook
from django_webhook.signals import SignalListener

from recoco.apps.projects.models import Project
from recoco.apps.projects.serializers import ProjectSerializer
from recoco.apps.survey.models import Answer
from recoco.apps.survey.serializers import AnswerSerializer


class WebhookSignalListener(SignalListener):
    def _site_ids(self, instance: Any) -> list[int]:
        if isinstance(instance, Project):
            return list(instance.sites.values_list("id", flat=True))
        if isinstance(instance, Answer):
            return list(instance.session.project.sites.values_list("id", flat=True))
        return []

    def find_webhooks(self, topic: str, instance: Any) -> list[tuple[int, str]]:
        if len(site_ids := self._site_ids(instance)) == 0:
            return []

        return list(
            Webhook.objects.filter(
                active=True,
                topics__name=topic,
                webhooksite__site__in=site_ids,
            ).values_list("id", "uuid")
        )

    def model_dict(self, instance: Any) -> dict[str, Any]:
        if isinstance(instance, Project):
            return ProjectSerializer(instance).data
        if isinstance(instance, Answer):
            return AnswerSerializer(instance).data
        return {}
