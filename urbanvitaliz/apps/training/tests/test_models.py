# encoding: utf-8

"""
Tests for training models

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-08-21 12:07:45 CEST
"""


import pytest
from django.utils import timezone
from model_bakery import baker

from .. import models


@pytest.mark.django_db
def test_challenge_is_open_by_default():
    challenge = baker.make(models.Challenge)
    assert models.Challenge.objects.first() == challenge
    assert models.Challenge.acquired_objects.count() == 0


@pytest.mark.django_db
def test_acquired_challenges_are_identified_in_manager():
    challenge = baker.make(models.Challenge, acquired_on=timezone.now())
    assert models.Challenge.acquired_objects.first() == challenge
    assert models.Challenge.objects.count() == 0


# eof
