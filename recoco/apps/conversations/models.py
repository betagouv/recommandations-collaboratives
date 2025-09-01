from django.contrib.auth import models as auth_models
from django.db import models
from model_utils.managers import InheritanceManager
from model_utils.models import TimeStampedModel

from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.projects import models as projects_models
from recoco.apps.tasks import models as tasks_models


class Message(TimeStampedModel):
    project = models.ForeignKey(
        projects_models.Project,
        on_delete=models.CASCADE,
        related_name="public_messages",
    )

    posted_by = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="project_messages"
    )

    in_reply_to = models.ForeignKey(
        "Message",
        on_delete=models.SET_NULL,
        related_name="replies",
        null=True,
        blank=True,
    )

    def serialize(self):
        payload = {
            "posted_by": self.posted_by_id,
            "created": self.created,
            "in_reply_to": self.in_reply_to,
            "nodes": [],
        }

        for node in (
            Node.objects.filter(message=self.pk)
            .order_by("position")
            .select_subclasses()
        ):
            payload["nodes"].append(node.serialize())

        return payload


class Node(models.Model):
    NODE_TYPE = "empty"

    objects = InheritanceManager()

    position = models.PositiveIntegerField()
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="nodes")

    def serialize(self):
        return {"type": self.NODE_TYPE, "position": self.position, "data": {}}


class MarkdownTextMixin(models.Model):
    text = models.TextField()

    def contribute_to_serialize(self, payload):
        payload["data"].update({"text": self.text})
        return payload

    class Meta:
        abstract = True


class MarkdownNode(Node, MarkdownTextMixin):
    NODE_TYPE = "markdown"

    def serialize(self):
        payload = super().serialize()

        payload = super().contribute_to_serialize(payload)

        return payload


class RecommendationNode(Node, MarkdownTextMixin):
    NODE_TYPE = "recommendation"

    recommendation = models.ForeignKey(tasks_models.Task, on_delete=models.CASCADE)

    def serialize(self):
        payload = super().serialize()

        payload = super().contribute_to_serialize(payload)
        payload["data"].update({"recommendation_id": self.recommendation.pk})

        return payload


class ContactNode(Node):
    NODE_TYPE = "vcard"

    contact = models.ForeignKey(addressbook_models.Contact, on_delete=models.CASCADE)

    def serialize(self):
        payload = super().serialize()

        payload["data"].update({"contact_id": self.contact.pk})

        return payload


class DocumentNode(Node):
    NODE_TYPE = "document"

    document = models.ForeignKey(projects_models.Document, on_delete=models.CASCADE)

    def serialize(self):
        payload = super().serialize()

        payload["data"].update({"document_id": self.document.pk})

        return payload
