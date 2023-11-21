# encoding: utf-8

"""
Models for reminders

author  : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-09-28 12:40:54 CEST
"""


from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone
from urbanvitaliz.apps.projects import models as projects_models


class ReminderManager(models.Manager):
    pass


class ReminderOnSiteManager(ReminderManager, CurrentSiteManager):
    pass


class ToSendReminderManager(models.Manager):
    """Manager for reminders to send"""

    def get_queryset(self):
        return super().get_queryset().filter(sent_on=None)


class ToSendReminderOnSiteManager(ToSendReminderManager, CurrentSiteManager):
    pass


class SentReminderManager(models.Manager):
    """Manager for sent reminders"""

    def get_queryset(self):
        return super().get_queryset().exclude(sent_on=None)


class SentReminderOnSiteManager(SentReminderManager, CurrentSiteManager):
    pass


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

    NEW_RECO = 0
    WHATS_UP = 1

    KIND_CHOICES = (
        (NEW_RECO, "Nouvelle Recommandation"),
        (WHATS_UP, "Où en êtes-vous ?"),
    )

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    objects = ReminderManager()
    sent = SentReminderManager()
    to_send = ToSendReminderManager()

    on_site = ReminderOnSiteManager()
    on_site_to_send = ToSendReminderOnSiteManager()
    on_site_sent = SentReminderOnSiteManager()

    deadline = models.DateField()

    project = models.ForeignKey(
        projects_models.Project, related_name="reminders", on_delete=models.CASCADE
    )

    state = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Etat d'avancement de la fréquence de ce rappels",
    )

    origin = models.IntegerField(choices=ORIGIN_CHOICES, default=0, editable=False)
    kind = models.IntegerField(choices=KIND_CHOICES, editable=False)

    sent_on = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        verbose_name = "rappel"
        verbose_name_plural = "rappels"

    def __str__(self):  # pragma: nocover
        return f"{self.project.name} - {self.kind} - {self.deadline}"

    def mark_as_sent(self):
        self.sent_on = timezone.now()
        self.save()


# eof
