"""
Tests for the ProConnect social account adapter.

Covers the account pre-hijacking scenario: an attacker self-signs up with the
victim's email and a password of their choice, without confirming the email.
When the victim later logs in via ProConnect, the identity is connected to that
account: the attacker's password must not give access to it afterwards.
"""

import pytest
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, RequestFactory
from django.urls import reverse
from model_bakery import baker

from .adapters import SocialAccountAdapter

EMAIL = "agent@collectivite.fr"
TEST_PASSWORD = "FakePassword12%"  # noqa: S105


def can_login_with_password():
    client = Client()
    client.post(reverse("account_login"), {"login": EMAIL, "password": TEST_PASSWORD})
    return auth.get_user(client).is_authenticated


def login_via_proconnect(current_site):
    request = RequestFactory().get("/")
    # setup needed middlewares
    SessionMiddleware(lambda r: None).process_request(request)
    MessageMiddleware(lambda r: None).process_request(request)
    request.site = current_site
    request.user = auth.models.AnonymousUser()

    sociallogin = SocialLogin(
        user=User(email=EMAIL, username=EMAIL),
        account=SocialAccount(provider="proconnect", uid="victim-sub", extra_data={}),
    )
    SocialAccountAdapter().pre_social_login(request, sociallogin)


def assert_proconnect_connected_to(user):
    assert (
        SocialAccount.objects.get(provider="proconnect", uid="victim-sub").user == user
    )
    assert EmailAddress.objects.get(user=user, email=EMAIL).verified


@pytest.mark.django_db
def test_proconnect_login_locks_out_unverified_account(current_site):
    user = baker.make(User, email=EMAIL)
    user.set_password(TEST_PASSWORD)
    user.save()
    assert not EmailAddress.objects.filter(
        user=user, email=EMAIL, verified=True
    ).exists()
    assert not can_login_with_password()

    login_via_proconnect(current_site)

    user.refresh_from_db()
    assert not user.has_usable_password()
    assert not can_login_with_password()
    assert_proconnect_connected_to(user)


@pytest.mark.django_db
def test_proconnect_login_keeps_password_of_verified_account(current_site):
    user = baker.make(User, email=EMAIL)
    user.set_password(TEST_PASSWORD)
    user.save()
    address, _ = EmailAddress.objects.get_or_create(user=user, email=user.email)
    address.verified = True
    address.save()
    assert can_login_with_password()

    login_via_proconnect(current_site)

    user.refresh_from_db()
    assert user.has_usable_password()
    assert can_login_with_password()
    assert_proconnect_connected_to(user)


@pytest.mark.django_db
def test_proconnect_login_without_local_account_does_nothing(current_site):
    login_via_proconnect(current_site)

    assert not User.objects.filter(username=EMAIL).exists()
    assert not SocialAccount.objects.exists()
