# encoding: utf-8

"""
Models for home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-11-15 14:44:55 CET

Inspired by django-gamification (https://github.com/mattjegan/django-gamification/)
"""


from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models
from django.utils import timezone


########################################################################
# Challenges definitions
########################################################################


class ChallengeDefinitionOnSiteManager(CurrentSiteManager):
    pass


class ChallengeDefinition(models.Model):
    objects = ChallengeDefinitionOnSiteManager()

    site = models.ForeignKey(site_models.Site, on_delete=models.CASCADE)
    code = models.SlugField(max_length=128)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    icon_name = models.CharField(null=True, blank=True, max_length=25)
    next_challenge = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.CASCADE
    )

    # TODO repeating the challenge definition after inactivity of n weeks
    # TODO inactivity or last acquired ?
    # TODO or 0 to tell show it every time
    week_inactivity_repeat = models.IntegerField(default=0)

    class Meta:
        unique_together = (("site", "code"),)

    def __str__(self):
        return self.name


########################################################################
# Tracking user challenges
########################################################################


class AcquiredChallengesManager(models.Manager):
    """Manager for acquired challenges"""

    def get_queryset(self):
        return super().get_queryset().exclude(acquired_on=None)


class OpenChallengesManager(models.Manager):
    """Manager for acquired challenges"""

    def get_queryset(self):
        return super().get_queryset().filter(acquired_on=None)


class Challenge(models.Model):
    """Challenge tracks the completion of users"""

    objects = OpenChallengesManager()
    acquired_objects = AcquiredChallengesManager()

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


# eof
