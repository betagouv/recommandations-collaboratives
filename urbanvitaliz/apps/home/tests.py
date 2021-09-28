# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-17 12:33:33 CEST
"""

import django.core.mail
import pytest
from django.conf import settings
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from urbanvitaliz.utils import login


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
def test_dashboard_not_available_for_non_staff_users(client):
    url = reverse("staff-dashboard")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_dashboard_available_for_staff_users(client):
    url = reverse("staff-dashboard")
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200


# eof
