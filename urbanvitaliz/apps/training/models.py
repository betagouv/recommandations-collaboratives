# encoding: utf-8

"""
Models for home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-11-15 14:44:55 CET

Inspired by django-gamification (https://github.com/mattjegan/django-gamification/)
"""


from django.contrib.auth import models as auth_models
from django.db import models
from django.utils import timezone


class ChallengeDefinition(models.Model):
    code = models.SlugField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    next_challenge = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            super().save(*args, **kwargs)

            # Update all Challenges that use this definition
            for challenge in Challenge.objects.filter(challenge_definition=self):
                challenge.name = self.name
                challenge.description = self.description

                if self.next_challenge:
                    challenge.next_challenge = Challenge.objects.filter(
                        challenge_definition=self.next_challenge
                    ).first()

                challenge.save()
        else:
            super().save(*args, **kwargs)


class ChallengeManager(models.Manager):
    """ """

    def create_challenge(self, definition):
        """
        Creates a new challenge from a challenge definition
        :param definition: ChallengeDefinition object
        :return: Challenge object
        """

        challenge = self.create(
            name=definition.name,
            description=definition.description,
            challenge_definition=definition,
        )
        if definition.next_challenge:
            challenge.next_challenge = self.filter(
                challenge_definition=definition.next_challenge
            ).first()
            challenge.save()
        return challenge


class AcquiredChallengesManager(ChallengeManager):
    """ """

    def get_queryset(self):
        return super().get_queryset().filter(acquired=True)


class Challenge(models.Model):
    challenge_definition = models.ForeignKey(
        ChallengeDefinition, on_delete=models.CASCADE
    )
    acquired = models.BooleanField(default=False)
    acquired_on = models.DateTimeField(
        default=timezone.now, verbose_name="Date d'acquisition"
    )

    def acquire(self):
        self.acquired = True
        self.acquired_on = timezone.now()
        self.save()

    user = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="training_challenges"
    )

    name = models.CharField(max_length=128, blank=True)
    description = models.TextField(null=True, blank=True)
    next_challenge = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.CASCADE
    )

    objects = ChallengeManager()
    acquired_objects = AcquiredChallengesManager()
