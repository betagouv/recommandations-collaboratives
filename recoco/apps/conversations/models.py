from datetime import datetime

from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.urls import reverse
from django.utils.http import urlencode
from markdownx.utils import markdownify
from model_utils.models import TimeStampedModel
from notifications.models import Notification
from polymorphic.models import PolymorphicModel

from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.projects import models as projects_models
from recoco.apps.tasks import models as tasks_models


class MessageNotDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)


class Message(TimeStampedModel):
    objects = models.Manager()
    not_deleted = MessageNotDeletedManager()

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
        url_no_query = reverse(
            "projects-project-detail-conversations",
            kwargs={"project_id": self.project.pk},
        )
        query_kwargs = {"message-id": self.pk}
        return f"{url_no_query}?{urlencode(query_kwargs)}"

    deleted = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        with transaction.atomic():
            self.deleted = datetime.now()
            for node in self.nodes.all():
                node.delete()
            self.save()


class Node(PolymorphicModel):
    class Meta:
        unique_together = ("position", "message")

    position = models.PositiveIntegerField()
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="nodes")

    def get_digest_recap(self):
        raise NotImplementedError()


class MarkdownTextMixin(models.Model):
    text = models.TextField()

    class Meta:
        abstract = True


class MarkdownNode(Node, MarkdownTextMixin):
    count_label = "message"

    def get_digest_recap(self):
        return {"type": "text", "text": self.text}


class RecommendationNode(Node, MarkdownTextMixin):
    recommendation = models.ForeignKey(tasks_models.Task, on_delete=models.CASCADE)
    count_label = "recommandation"

    def get_digest_recap(self):
        res = {"type": "recommendation"}

        if self.recommendation.resource is None:
            res = res | {
                "text": markdownify(self.text),
                "title": self.recommendation.intent,
            }
        else:
            res = res | {
                "title": self.recommendation.resource.title,
                "subtitle": self.recommendation.resource.subtitle,
                "text": markdownify(self.text),
            }
        return res


class ContactNode(Node):
    contact = models.ForeignKey(addressbook_models.Contact, on_delete=models.CASCADE)
    count_label = "contact"

    def get_digest_recap(self):
        c: addressbook_models.Contact = self.contact
        return {
            "type": "contact",
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "phone_no": c.phone_no,
            "mobile_no": c.mobile_no,
            "function": c.division,
            "organization_name": c.organization.name,
        }


class DocumentNode(Node):
    document = models.ForeignKey(projects_models.Document, on_delete=models.CASCADE)
    count_label = "document"

    def save(self, **kwargs):
        with transaction.atomic():
            super().save(**kwargs)
            self.document.deleted = None
            self.document.attached_object = self.message
            self.document.save()

    def delete(self, **kwargs):
        with transaction.atomic():
            self.document.soft_delete()
            super().delete(**kwargs)

    def get_digest_recap(self):
        d: projects_models.Document = self.document
        return {"type": "document", "name": d.filename()}
