import datetime

import pytest
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from model_bakery import baker

from .. import models, utils


@pytest.mark.django_db
def test_get_challenge_with_non_existing_definition(request):
    user = baker.make(auth_models.User)
    assert utils.get_challenge_for(user, "unknown-code-name") is None


@pytest.mark.django_db
def test_get_challenge_with_other_site_definition(request):
    user = baker.make(auth_models.User)
    baker.make(models.ChallengeDefinition, code="a-code")
    assert utils.get_challenge_for(user, "a-code") is None


@pytest.mark.django_db
def test_user_challenge_returned_when_open_one_exists():
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User, last_login=timezone.now())
    definition = baker.make(models.ChallengeDefinition, site=site, code="a-code")
    challenge = baker.make(models.Challenge, challenge_definition=definition, user=user)

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # nothing new under the sun
    assert current == challenge


@pytest.mark.django_db
def test_user_challenge_returned_now_one_for_every_time_challenge():
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User, last_login=timezone.now())
    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=0
    )
    challenge = baker.make(
        models.Challenge,
        challenge_definition=definition,
        user=user,
        acquired_on=timezone.now(),
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # a new challenge is born
    assert current and current != challenge and current.acquired_on is None


@pytest.mark.django_db
def test_user_challenge_not_repeated_before_inactivity_period():
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User, last_login=timezone.now())
    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=1
    )
    challenge = baker.make(
        models.Challenge,
        challenge_definition=definition,
        user=user,
        acquired_on=timezone.now(),
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # no active challenge
    assert current is None


@pytest.mark.django_db
def test_user_challenge_repeated_when_over_inactivity_period():
    last_week = timezone.now() - datetime.timedelta(days=8)
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User, last_login=last_week)
    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=1
    )
    challenge = baker.make(
        models.Challenge,
        challenge_definition=definition,
        user=user,
        acquired_on=last_week,
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # a new challenge is born
    assert current and current != challenge and current.acquired_on is None


# eof
