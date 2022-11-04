from django import template

from .. import utils
from ..models import Challenge

register = template.Library()


@register.simple_tag
def challenge_for(user, codename):
    return utils.get_challenge_for(user, codename)


@register.simple_tag
def challenge_acquire(challenge):
    challenge.acquire()
    return ""


@register.simple_tag
def get_challenges_for(user, acquired=True):
    challenges = Challenge.objects.order_by("acquired", "-acquired_on").filter(
        user=user
    )
    if acquired is not None:
        challenges = challenges.filter(acquired=acquired)

    return challenges
