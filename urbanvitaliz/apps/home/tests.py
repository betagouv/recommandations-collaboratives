# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-17 12:33:33 CEST
"""

import django.core.mail
import pytest
from django import forms
from django.conf import settings
from django.contrib.auth import models as auth
from django.db.utils import IntegrityError
from django.urls import reverse
from model_bakery import baker
from pytest_django.asserts import assertRedirects
from urbanvitaliz.utils import login

from . import utils

#
# create new user hook for magicauth


@pytest.mark.django_db
def test_create_user_with_proper_email():
    email = "new.user@example.com"
    user = utils.create_user(email)
    assert user.email == email
    assert user.username == email
    assert user.profile


@pytest.mark.django_db
def test_create_user_fails_with_missing_email():
    email = None
    with pytest.raises(forms.ValidationError):
        utils.create_user(email)


@pytest.mark.django_db
def test_create_user_fails_for_known_email():
    email = "known.user@example.com"
    baker.make(auth.User, username=email)
    with pytest.raises(IntegrityError):
        utils.create_user(email)


#
# seding message to team


def test_user_can_access_contact_form(client):

    url = reverse("home-contact") + "?next=/"
    response = client.get(url)

    assert b"<form " in response.content


@pytest.mark.django_db
def test_non_logged_user_can_send_message_to_team(mocker, client):

    mocker.patch("django.core.mail.send_mail")

    data = {"subject": "a subject", "content": "some content"}
    url = reverse("home-contact") + "?next=/"
    response = client.post(url, data=data)

    django.core.mail.send_mail.assert_called_once_with(
        subject=data["subject"],
        message=data["content"],
        from_email=settings.EMAIL_FROM,
        recipient_list=settings.TEAM_EMAILS,
        fail_silently=True,
    )

    assertRedirects(response, "/")


@pytest.mark.django_db
def test_logged_user_can_send_message_to_team(mocker, client):

    mocker.patch("django.core.mail.send_mail")

    data = {"subject": "a subject", "content": "some content"}
    url = reverse("home-contact") + "?next=/"
    with login(client, is_staff=False) as user:
        response = client.post(url, data=data)

    content = data["content"] + f"\n\nfrom: {user.email}"

    django.core.mail.send_mail.assert_called_once_with(
        subject=data["subject"],
        message=content,
        from_email=settings.EMAIL_FROM,
        recipient_list=settings.TEAM_EMAILS,
        fail_silently=True,
    )

    assertRedirects(response, "/")


########################################################################
# Dashboard
########################################################################


@pytest.mark.django_db
def test_dashboard_not_available_for_non_switchtender_users(client):
    url = reverse("switchtender-dashboard")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_dashboard_available_for_switchtender_users(client):
    url = reverse("switchtender-dashboard")
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


########################################################################
# Statistics
########################################################################


@pytest.mark.django_db
def test_user_can_access_stats(client):
    url = reverse("statistics")
    response = client.get(url)
    assert response.status_code == 200


#######################################################################
# Static pages
#######################################################################


def test_user_can_access_methodology(client):
    url = reverse("methodology")
    response = client.get(url)
    assert response.status_code == 200


def test_user_can_access_whoweare(client):
    url = reverse("whoweare")
    response = client.get(url)
    assert response.status_code == 200


def test_user_can_access_followus(client):
    url = reverse("followus")
    response = client.get(url)
    assert response.status_code == 200


# eof
