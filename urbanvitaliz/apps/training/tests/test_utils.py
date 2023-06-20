import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker

from .. import models, utils


@pytest.mark.django_db
def test_get_challenge_with_non_existing_definition(request):
    user = baker.make(auth.User)
    assert utils.get_challenge_for(user, "unknown-code-name") is None


@pytest.mark.django_db
def test_get_challenge_with_other_site_definition(request):
    user = baker.make(auth.User)
    baker.make(models.ChallengeDefinition, code="nice-code")
    assert utils.get_challenge_for(user, "unknown-code-name") is None


@pytest.mark.django_db
def test_get_challenge_with_existing_definition(request):
    site = get_current_site(request)
    user = baker.make(auth.User)
    baker.make(models.ChallengeDefinition, site=site, code="nice-code")

    challenge = utils.get_challenge_for(user, "nice-code")
    assert challenge is not None
    assert models.Challenge.objects.count() == 1
    assert challenge.acquired_on is None


@pytest.mark.django_db
def test_get_challenge_multiple_times(request):
    site = get_current_site(request)
    user = baker.make(auth.User)
    baker.make(models.ChallengeDefinition, site=site, code="nice-code")
    utils.get_challenge_for(user, "nice-code")
    challenge = utils.get_challenge_for(user, "nice-code")
    assert challenge is not None
    assert models.Challenge.objects.count() == 1
    assert challenge.acquired_on is None
