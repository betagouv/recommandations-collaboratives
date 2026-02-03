# encoding: utf-8

"""
Utility functions for training

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-08-21 14:28:45 CEST
"""

import datetime

from django.utils import timezone

from . import models


def get_challenge_for(user, codename):
    """Return existing open challenge, new one if necessary, or None"""
    try:
        challenge_definition = models.ChallengeDefinition.objects.get(code=codename)
    except models.ChallengeDefinition.DoesNotExist:
        return None

    challenge = models.Challenge.objects.filter(
        challenge_definition=challenge_definition, user=user
    ).last()

    if not challenge:
        # Create a new challenge
        return models.Challenge.objects.create(
            challenge_definition=challenge_definition, user=user
        )
    if challenge.snoozed_on:
        snoozed_days = (timezone.now() - challenge.snoozed_on).days
        repetition = challenge_definition.week_inactivity_repeat * 7
        if repetition == 0:
            return None
        if snoozed_days > repetition:
            return challenge
        return None

    if challenge.acquired_on:
        last_month = timezone.now() - datetime.timedelta(weeks=4)
        if (
            user.profile.previous_activity_at
            and user.profile.previous_activity_at < last_month
        ) and challenge.acquired_on < last_month:
            challenge.acquired_on = None
            challenge.save()
            return challenge
        return None

    return challenge


# eof
