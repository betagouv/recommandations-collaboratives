# encoding: utf-8

"""
Models for reminders

author  : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-09-28 12:40:54 CEST
"""


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from urbanvitaliz.apps.communication import models as communication_models


class ReminderManager(models.Manager):
    """Manager for reminders to send"""

    def get_queryset(self):
        return super().get_queryset().filter(sent_on=None)


class SentReminderManager(models.Manager):
    """Manager for sent reminders"""

    def get_queryset(self):
        return super().get_queryset().exclude(sent_on=None)


class Reminder(models.Model):
    """Represents a reminder to be sent on a given date"""

    SYSTEM = 0
    SELF = 1
    STAFF = 2

    ORIGIN_CHOICES = (
        (SYSTEM, "Système"),
        (SELF, "Personal"),
        (STAFF, "Assigned"),
    )

    to_send = ReminderManager()
    sent = SentReminderManager()

    recipient = models.CharField(max_length=128)

    deadline = models.DateField()

    # django method (deprecated)
    subject = models.TextField(default="", blank=True)
    text = models.TextField(default="", blank=True)
    html = models.TextField(default="", blank=True)

    # SendInBlue
    template = models.ForeignKey(
        communication_models.EmailTemplate,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    template_params = models.JSONField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(default=0)
    related = GenericForeignKey("content_type", "object_id")

    origin = models.IntegerField(choices=ORIGIN_CHOICES, default=0)

    sent_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "rappel"
        verbose_name_plural = "rappels"

    def __str__(self):  # pragma: nocover
        return f"{self.recipient} {self.deadline}"

    def mark_as_sent(self):
        self.sent_on = timezone.now()
        self.save()


# eof
