# encoding: utf-8

"""
Tests for invite application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-04-20 10:11:56 CEST
"""


import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertNotContains
from urbanvitaliz.utils import login

from . import models


################################################################
# Invite details
################################################################
@pytest.mark.django_db
def test_invite_available_for_everyone(request, client):
    invite = Recipe(models.Invite, site=get_current_site(request)).make()
    url = reverse("invites-invite-details", args=[invite.pk])
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_invite_show_error_message_if_not_for_current_logged_in_user(request, client):
    invite = Recipe(models.Invite, site=get_current_site(request)).make()
    url = reverse("invites-invite-details", args=[invite.pk])

    with login(client):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "Désolé")


@pytest.mark.django_db
def test_invite_does_not_match_existing_account(request, client):
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite, site=get_current_site(request), email=invited.email
    ).make()
    url = reverse("invites-invite-details", args=[invite.pk])

    with login(client):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "Désolé")


@pytest.mark.django_db
def test_invite_matches_existing_account_for_logged_in_user(request, client):
    with login(client) as user:
        invite = Recipe(
            models.Invite, site=get_current_site(request), email=user.email
        ).make()
        url = reverse("invites-invite-details", args=[invite.pk])
        response = client.get(url)

    assert response.status_code == 200
    assertNotContains(response, "Désolé")


@pytest.mark.django_db
def test_invite_matches_existing_account_redirects_anonyous_user_to_login(
    request, client
):
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite, site=get_current_site(request), email=invited.email
    ).make()

    url = reverse("invites-invite-details", args=[invite.pk])
    response = client.get(url)

    assert response.status_code == 302


################################################################
# Invite accepts
################################################################
@pytest.mark.django_db
def test_accept_invite_returns_to_details_if_get(request, client):
    invite = Recipe(models.Invite, site=get_current_site(request)).make()
    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.get(url)

    assert response.status_code == 302
    assert invite.accepted_on is None


@pytest.mark.django_db
def test_accept_invite_matches_existing_account(request, client):
    with login(client) as user:
        invite = Recipe(
            models.Invite, site=get_current_site(request), email=user.email
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_without_existing_account(
    request,
    client,
):
    with login(client, email="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            site=get_current_site(request),
            email="whatever@wherever.com",
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is None
    assert user not in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_switchtender_with_matching_existing_account(
    request,
    client,
):
    with login(client, email="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            site=get_current_site(request),
            role="SWITCHTENDER",
            email=user.email,
            project__name="project",
            project__location="here",
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert user not in invite.project.members.all()
    assert user == invite.project.switchtenders_on_site.first().switchtender


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_switchtender_with_mismatched_existing_account(
    request,
    client,
):
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite,
        site=get_current_site(request),
        email=invited.email,
    ).make()

    with login(client, email="invited@here.tld") as user:
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is None
    assert user not in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_collaborator_with_matching_existing_account(
    request,
    client,
):
    with login(client, email="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            role="COLLABORATOR",
            site=get_current_site(request),
            email=user.email,
            project__name="project",
            project__location="here",
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert user in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_collaborator_with_mismatched_existing_account(
    request,
    client,
):
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        site=get_current_site(request),
        email=invited.email,
    ).make()

    with login(client, email="invited@here.tld") as user:
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is None
    assert user not in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()


@pytest.mark.django_db
def test_anonymous_accepts_invite_with_existing_account(
    request,
    client,
):
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        site=get_current_site(request),
        email=invited.email,
    ).make()

    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is None
    assert invite.project.members.count() == 0
    assert invite.project.switchtenders.count() == 0


@pytest.mark.django_db
def test_anonymous_accepts_invite_as_switchtender(
    request,
    client,
):
    invite = Recipe(
        models.Invite,
        role="SWITCHTENDER",
        site=get_current_site(request),
        email="a@new.one",
    ).make()

    data = {
        "first_name": "First",
        "last_name": "Last",
        "organization": "Some Organization",
        "position": "Doing Stuff",
    }

    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.post(url, data=data)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert invite.project.members.count() == 0
    assert invite.project.switchtenders_on_site.count() == 1

    user = auth_models.User.objects.get(email=invite.email)
    assert user.username == invite.email
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert user.profile.organization.name == data["organization"]
    assert user.profile.organization_position == data["position"]
