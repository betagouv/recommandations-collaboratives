import datetime

import pytest
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.utils import timezone
from model_bakery import baker

from .. import models, utils


@pytest.mark.django_db
def test_get_challenge_with_non_existing_definition(request):
    user = baker.make(auth_models.User)
    assert utils.get_challenge_for(user, "unknown-code-name") is None


@pytest.mark.django_db
@pytest.mark.skip
def test_get_challenge_with_other_site_definition(request):
    user = baker.make(auth_models.User)
    baker.make(models.ChallengeDefinition, code="a-code")
    assert utils.get_challenge_for(user, "a-code") is None


@pytest.mark.django_db
def test_user_challenge_returned_when_first_visit():
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User)
    definition = baker.make(models.ChallengeDefinition, site=site, code="a-code")

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # new challenge is proposed
    assert current


@pytest.mark.django_db
def test_user_challenge_returned_when_is_snoozed_and_repeat_exceed():
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User, last_login=timezone.now())
    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=3
    )
    last_month = timezone.now() - datetime.timedelta(weeks=4)
    challenge = baker.make(
        models.Challenge,
        challenge_definition=definition,
        user=user,
        snoozed_on=last_month,
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # challenge is proposed
    assert current and current == challenge


@pytest.mark.django_db
def test_user_challenge_not_returned_when_is_snoozed_and_repeat_set_to_zero_week():
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User, last_login=timezone.now())
    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=0
    )
    last_month = timezone.now() - datetime.timedelta(weeks=4)
    baker.make(
        models.Challenge,
        challenge_definition=definition,
        user=user,
        snoozed_on=last_month,
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # challenge is not proposed
    assert current is None


@pytest.mark.django_db
def test_get_acquired_challenge_when_user_has_no_previous_login():
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User, last_login=timezone.now())
    user.profile.previous_login_at = None
    user.profile.save()

    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=4
    )

    baker.make(
        models.Challenge,
        user=user,
        challenge_definition=definition,
        acquired_on=datetime.datetime.now() - datetime.timedelta(weeks=1),
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # challenge is not proposed
    assert current is None


@pytest.mark.django_db
def test_user_challenge_not_returned_when_is_snoozed_and_repeat_not_exceeded():
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User, last_login=timezone.now())
    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=3
    )
    last_weeks = timezone.now() - datetime.timedelta(weeks=2)
    baker.make(
        models.Challenge,
        challenge_definition=definition,
        user=user,
        snoozed_on=last_weeks,
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # challenge is not proposed
    assert current is None


@pytest.mark.django_db
def test_user_challenge_returned_when_is_not_acquired():
    site = baker.make(site_models.Site)
    user = baker.make(auth_models.User, last_login=timezone.now())
    definition = baker.make(models.ChallengeDefinition, site=site, code="a-code")
    challenge = baker.make(models.Challenge, challenge_definition=definition, user=user)

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # challenge is proposed
    assert current and current == challenge and current.acquired_on is None


@pytest.mark.django_db
def test_user_challenge_returned_when_inactivity_more_than_one_month():
    site = baker.make(site_models.Site)
    more_than_one_month = timezone.now() - datetime.timedelta(weeks=5)
    user = baker.make(auth_models.User, last_login=more_than_one_month)
    user.profile.previous_login_at = more_than_one_month
    user.profile.save()

    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=3
    )
    challenge = baker.make(
        models.Challenge,
        challenge_definition=definition,
        user=user,
        acquired_on=more_than_one_month,
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # challenge is proposed
    assert current and current == challenge and current.acquired_on is None


@pytest.mark.django_db
def test_user_challenge_not_returned_when_inactivity_less_than_one_month():
    site = baker.make(site_models.Site)
    more_than_one_month = timezone.now() - datetime.timedelta(weeks=5)
    less_than_one_month = timezone.now() - datetime.timedelta(weeks=3)
    user = baker.make(auth_models.User, last_login=less_than_one_month)
    user.profile.previous_login_at = less_than_one_month
    user.profile.save()

    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=3
    )
    baker.make(
        models.Challenge,
        challenge_definition=definition,
        user=user,
        acquired_on=more_than_one_month,
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # challenge is not proposed
    assert current is None


@pytest.mark.django_db
def test_user_challenge_not_returned_when_inactivity_but_acquired_less_than_one_month():
    site = baker.make(site_models.Site)
    more_than_one_month = timezone.now() - datetime.timedelta(weeks=5)
    less_than_one_month = timezone.now() - datetime.timedelta(weeks=3)
    user = baker.make(auth_models.User, last_login=more_than_one_month)
    user.profile.previous_login_at = more_than_one_month
    user.profile.save()

    definition = baker.make(
        models.ChallengeDefinition, site=site, code="a-code", week_inactivity_repeat=3
    )
    baker.make(
        models.Challenge,
        challenge_definition=definition,
        user=user,
        acquired_on=less_than_one_month,
    )

    with settings.SITE_ID.override(site.pk):
        current = utils.get_challenge_for(user, definition.code)

    # challenge is not proposed
    assert current is None


# eof
