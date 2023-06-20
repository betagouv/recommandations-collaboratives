# encoding: utf-8

"""
Testing the training api

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2023-06-20 14:10:36 CEST
"""

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient


from .. import models

########################################################################
# get challenge
########################################################################


@pytest.mark.django_db
def test_anonymous_cannot_use_challenge_get_api(request, client):
    site = get_current_site(request)
    definition = baker.make(models.ChallengeDefinition, site=site)

    client = APIClient()

    url = reverse("challenges-challenge", args=[definition.code])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_challenge_get_api_returns_new_challenge_info(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    definition = baker.make(models.ChallengeDefinition, site=site)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("challenges-challenge", args=[definition.code])
    response = client.get(url)

    assert response.status_code == 200

    assert response.data["acquired_on"] is None
    assert dict(response.data["challenge_definition"]) == {
        "name": definition.name,
        "code": definition.code,
        "description": definition.description,
        "icon_name": None,
        "next_challenge": None,
    }


@pytest.mark.django_db
def test_challenge_get_api_returns_existing_challenge_info(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    definition = baker.make(models.ChallengeDefinition, site=site)
    challenge = baker.make(models.Challenge, user=user, challenge_definition=definition)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("challenges-challenge", args=[definition.code])
    response = client.get(url)

    assert response.status_code == 200

    assert response.data["acquired_on"] is challenge.acquired_on
    assert dict(response.data["challenge_definition"]) == {
        "name": definition.name,
        "code": definition.code,
        "description": definition.description,
        "icon_name": None,
        "next_challenge": None,
    }


########################################################################
# patch challenge
########################################################################


@pytest.mark.django_db
def test_anonymous_cannot_use_challenge_patch_api(request, client):
    site = get_current_site(request)
    definition = baker.make(models.ChallengeDefinition, site=site)

    data = {}

    client = APIClient()

    url = reverse("challenges-challenge", args=[definition.code])
    response = client.patch(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_challenge_patch_api_fails_for_missing_challenge(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    definition = baker.make(models.ChallengeDefinition, site=site)

    data = {}

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("challenges-challenge", args=[definition.code])
    response = client.patch(url, data=data)

    assert response.status_code == 404


@pytest.mark.django_db
def test_challenge_patch_api_updates_challenge(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    definition = baker.make(models.ChallengeDefinition, site=site)
    challenge = baker.make(models.Challenge, user=user, challenge_definition=definition)

    data = {}

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("challenges-challenge", args=[definition.code])
    response = client.patch(url, data=data)

    assert response.status_code == 200

    challenge.refresh_from_db()

    assert challenge.acquired_on is not None

    assert response.data["acquired_on"] is not None
    assert dict(response.data["challenge_definition"]) == {
        "name": definition.name,
        "code": definition.code,
        "description": definition.description,
        "icon_name": None,
        "next_challenge": None,
    }


# eof
