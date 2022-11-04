from .models import Challenge, ChallengeDefinition


def get_challenge_for(user, codename):
    """Return a challenge or create it for the given user"""
    try:
        challenge_definition = ChallengeDefinition.objects.get(code=codename)

    except ChallengeDefinition.DoesNotExist:
        return None

    challenge, created = Challenge.objects.get_or_create(
        user=user, challenge_definition=challenge_definition
    )
    return challenge
