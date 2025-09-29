from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from model_utils.models import TimeStampedModel
from notifications.models import Notification
from polymorphic.models import PolymorphicModel

from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.projects import models as projects_models
from recoco.apps.tasks import models as tasks_models


class Message(TimeStampedModel):
    project = models.ForeignKey(
        projects_models.Project,
        on_delete=models.CASCADE,
        related_name="public_messages",
    )

    notifications = GenericRelation(
        Notification,
        content_type_field="action_object_content_type_id",
        object_id_field="action_object_object_id",
        related_query_name="action_messages",
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

    def get_absolute_url(self):
        return reverse(
            "projects-project-detail-conversations",
            kwargs={"project_id": self.project.pk},
            query={"message-id": self.pk},
        )


class Node(PolymorphicModel):
    position = models.PositiveIntegerField()
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="nodes")


class MarkdownTextMixin(models.Model):
    text = models.TextField()

    class Meta:
        abstract = True


class MarkdownNode(Node, MarkdownTextMixin):
    pass


class RecommendationNode(Node, MarkdownTextMixin):
    recommendation = models.ForeignKey(tasks_models.Task, on_delete=models.CASCADE)


class ContactNode(Node):
    contact = models.ForeignKey(addressbook_models.Contact, on_delete=models.CASCADE)


class DocumentNode(Node):
    document = models.ForeignKey(projects_models.Document, on_delete=models.CASCADE)
