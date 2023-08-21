# encoding: utf-8

"""
template tags for training

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-08-21 14:54:48 CEST
"""


from django import template
from django.utils import timezone

from .. import models, utils

register = template.Library()


@register.simple_tag
def challenge_for(user, codename):
    """Return challenge with codename for given user"""
    return utils.get_challenge_for(user, codename)


@register.simple_tag
def challenge_acquire(challenge):
    # TODO why isn't challenge object saved ?
    challenge.acquired_on = timezone.now()
    return ""


@register.simple_tag
def get_challenges_for(user, acquired=None):
    """Return acquired challenges for user"""
    return models.Challenge.acquired_objects.order_by("-acquired_on").filter(user=user)


# eof
