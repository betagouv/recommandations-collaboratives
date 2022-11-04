from django import template

from ..models import Challenge, ChallengeDefinition

register = template.Library()


@register.simple_tag
def challenge_for(user, codename):
    try:
        challenge_definition = ChallengeDefinition.objects.get(code=codename)

    except ChallengeDefinition.DoesNotExist:
        return None

    challenge, created = Challenge.objects.get_or_create(
        user=user, challenge_definition=challenge_definition
    )
    return challenge


@register.simple_tag
def challenge_acquire(challenge):
    challenge.acquire()
    return ""


@register.simple_tag
def get_challenges_for(user, acquired=True):
    return Challenge.objects.filter(user=user, acquired=acquired)
