# encoding: utf-8

"""
Models for home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-11-15 14:44:55 CET

Inspired by django-gamification (https://github.com/mattjegan/django-gamification/)
"""


from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.db import models


class ChallengeDefinitionOnSiteManager(CurrentSiteManager):
    pass


class ChallengeDefinition(models.Model):
    objects = ChallengeDefinitionOnSiteManager()

    site = models.ForeignKey(site_models.Site, on_delete=models.CASCADE)
    code = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    icon_name = models.CharField(null=True, blank=True, max_length=25)
    next_challenge = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class AcquiredChallengesManager(models.Manager):
    """ """

    def get_queryset(self):
        return super().get_queryset().exclude(acquired=None)


class Challenge(models.Model):
    challenge_definition = models.ForeignKey(
        ChallengeDefinition, on_delete=models.CASCADE
    )
    started_on = models.DateTimeField(
        verbose_name="Date de démarrage", default=None, null=True
    )
    acquired_on = models.DateTimeField(
        verbose_name="Date d'acquisition", default=None, null=True
    )

    user = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="training_challenges"
    )

    objects = models.Manager()
    acquired_objects = AcquiredChallengesManager()

    class Meta:
        unique_together = (("challenge_definition", "user"),)
