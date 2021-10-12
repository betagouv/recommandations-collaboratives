# encoding: utf-8

"""
Models for reminders

author  : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-09-28 12:40:54 CEST
"""


from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone


class MailManager(models.Manager):
    """Manager for mails to send"""

    def get_queryset(self):
        return super().get_queryset().filter(sent_on=None)


class SentMailManager(models.Manager):
    """Manager for sent mails"""

    def get_queryset(self):
        return super().get_queryset().exclude(sent_on=None)


class Mail(models.Model):
    """Represents a mail to be sent on a given date"""

    SELF = 1
    STAFF = 2

    ORIGIN_CHOICES = (
        (SELF, "Personal"),
        (STAFF, "Assigned"),
    )

    to_send = MailManager()
    sent = SentMailManager()

    recipient = models.CharField(max_length=128)
    subject = models.TextField(default="")
    text = models.TextField(default="")
    html = models.TextField(default="")
    deadline = models.DateField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related = GenericForeignKey("content_type", "object_id")

    origin = models.IntegerField(choices=ORIGIN_CHOICES, default=0)

    sent_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "mail"
        verbose_name_plural = "mails"

    def __str__(self):  # pragma: nocover
        return f"{self.recipient} {self.deadline}"

    def mark_as_sent(self):
        self.sent_on = timezone.now()
        self.save()


# eof
