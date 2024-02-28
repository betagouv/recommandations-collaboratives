# encoding: utf-8

"""
Models for communication

author  : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-12-21 12:40:54 CEST
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models


class EmailTemplate(models.Model):
    class Meta:
        unique_together = ("site", "name")

    NAME_CHOICES = (
        ("project_received", "Projet bien reçu"),
        ("project_accepted", "Projet accepté par l'équipe de modération"),
        # ("project_reminders_digest", "Résumé des rappels"),
        ("digest_for_non_switchtender", "Résumé quotidien général de notifications"),
        ("digest_for_switchtender", "Résumé quotidien des conseillers"),
        ("new_recommendations_digest", "Résumé des nouvelles recommandations"),
        (
            "new_site_for_switchtender",
            "Alerte conseillers d'un nouveau projet sur le territoire",
        ),
        ("sharing_invitation", "Invitation à rejoindre un projet"),
        (
            "project_reminders_new_reco_digest",
            "Rappel des nouvelles recommandations (mail projet B)",
        ),
        ("project_reminders_whats_up_digest", "Où en êtes-vous ? (mail projet C)"),
    )

    objects = models.Manager()
    on_site = CurrentSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, choices=NAME_CHOICES)
    sib_id = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.sib_id}"


class TransactionRecord(models.Model):
    """
    A record of a transaction (mostly a one shot sent email)
    """

    objects = models.Manager()
    on_site = CurrentSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    sent_on = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=65536)
    label = models.CharField(blank=True, unique=False, max_length=2048)

    faked = models.BooleanField(
        default=False, editable=False, help_text="If this sent was faked"
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    related_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="An non-user object related to this transaction",
        null=True,
        blank=True,
    )
    related_id = models.PositiveIntegerField(null=True, blank=True)
    related = GenericForeignKey("related_ct", "related_id")


# eof
