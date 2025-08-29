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

    def serialize(self):
        payload = {"posted_by": self.posted_by_id, "nodes": []}

        for node in Node.objects.filter(message=self.pk).select_subclasses():
            payload["nodes"].append(node.serialize())

        return payload


class Node(models.Model):
    objects = InheritanceManager()

    position = models.PositiveIntegerField()
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="nodes")


class MarkdownNode(Node):
    text = models.TextField()

    def serialize(self):
        return {"type": "markdown", "text": self.text}


class RecommendationNode(Node):
    recommendation = models.ForeignKey(tasks_models.Task, on_delete=models.CASCADE)


class ContactNode(Node):
    contact = models.ForeignKey(addressbook_models.Contact, on_delete=models.CASCADE)


class DocumentNode(Node):
    document = models.ForeignKey(projects_models.Document, on_delete=models.CASCADE)
