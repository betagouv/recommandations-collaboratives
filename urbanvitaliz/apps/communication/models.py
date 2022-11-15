# encoding: utf-8

"""
Models for communication

author  : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-12-21 12:40:54 CEST
"""

from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models


class EmailTemplate(models.Model):
    class Meta:
        unique_together = ("site", "name")

    NAME_CHOICES = (
        ("project_accepted", "Projet accepté par l'équipe de modération"),
        ("project_reminders_digest", "Résumé des rappels"),
        ("digest_for_non_switchtender", "Résumé quotidien général de notifications"),
        ("digest_for_switchtender", "Résumé quotidien des conseillers"),
        ("new_recommendations_digest", "Résumé des nouvelles recommandations"),
        (
            "new_site_for_switchtender",
            "Alerte conseillers d'un nouveau projet sur le territoire",
        ),
        ("sharing invitation", "Invitation à rejoindre un projet"),
    )

    objects = models.Manager()
    on_site = CurrentSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, choices=NAME_CHOICES)
    sib_id = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.sib_id}"


# eof
