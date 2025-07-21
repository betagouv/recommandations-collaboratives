from typing import Any

from django_webhook.models import Webhook
from django_webhook.signals import SignalListener
from taggit.models import TaggedItem

from recoco.apps.projects.models import Project
from recoco.apps.projects.serializers import ProjectSerializer
from recoco.apps.survey.models import Answer
from recoco.apps.survey.serializers import AnswerSerializer
from recoco.apps.tasks.models import Task
from recoco.apps.tasks.serializers import TaskWebhookSerializer


class WebhookSignalListener(SignalListener):
    def _site_ids(self, instance: Any) -> list[int]:
        if isinstance(instance, Project):
            return list(instance.sites.values_list("id", flat=True))
        if isinstance(instance, Answer):
            return list(instance.session.project.sites.values_list("id", flat=True))
        if isinstance(instance, TaggedItem):
            if isinstance(project := instance.content_object, Project):
                return list(project.sites.values_list("id", flat=True))
            return []
        if isinstance(instance, Task):
            return [instance.site.id]

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
        kwargs = {"context": {"request": None}}

        if isinstance(instance, Project):
            return ProjectSerializer(instance, **kwargs).data
        if isinstance(instance, Answer):
            return AnswerSerializer(instance, **kwargs).data
        if isinstance(instance, TaggedItem):
            if isinstance(project := instance.content_object, Project):
                return ProjectSerializer(project, **kwargs).data
        if isinstance(instance, Task):
            return TaskWebhookSerializer(instance, **kwargs).data

        return {}
