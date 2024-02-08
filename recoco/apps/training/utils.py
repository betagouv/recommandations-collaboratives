# encoding: utf-8

"""
Utility functions for training

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-08-21 14:28:45 CEST
"""


from django.utils import timezone

from . import models


def get_challenge_for(user, codename):
    """Return existing open challenge, new one if necessary, or None"""
    try:
        challenge_definition = models.ChallengeDefinition.objects.get(code=codename)
    except models.ChallengeDefinition.DoesNotExist:
        return None

    try:
        return models.Challenge.objects.get(
            challenge_definition=challenge_definition, user=user
        )
    except models.Challenge.DoesNotExist:
        pass  # it's ok, let look if a new one is required

    # should we repeat ?
    inactivity = (timezone.now() - user.last_login).days
    repetition = challenge_definition.week_inactivity_repeat * 7
    if inactivity < repetition:
        return None  # do not repeat for the moment

    # Start a new challenge
    return models.Challenge.objects.create(
        challenge_definition=challenge_definition, user=user
    )


# eof
