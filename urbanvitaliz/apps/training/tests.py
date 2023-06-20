import pytest
from django.contrib.auth import models as auth
from model_bakery import baker

from .models import Challenge, ChallengeDefinition
from .utils import get_challenge_for


@pytest.mark.django_db
def test_get_challenge_with_non_existing_definition(request):
    user = baker.make(auth.User)
    assert get_challenge_for(user, "unknown-code-name") is None


@pytest.mark.django_db
def test_get_challenge_with_existing_definition(request):
    user = baker.make(auth.User)
    baker.make(ChallengeDefinition, code="nice-code")

    challenge = get_challenge_for(user, "nice-code")
    assert challenge is not None
    assert Challenge.objects.count() == 1
    assert challenge.acquired_on is None


@pytest.mark.django_db
def test_get_challenge_multiple_times(request):
    user = baker.make(auth.User)
    baker.make(ChallengeDefinition, code="nice-code")
    get_challenge_for(user, "nice-code")
    challenge = get_challenge_for(user, "nice-code")
    assert challenge is not None
    assert Challenge.objects.count() == 1
    assert challenge.acquired_on is None
