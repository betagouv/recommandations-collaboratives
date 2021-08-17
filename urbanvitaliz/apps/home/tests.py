# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-17 12:33:33 CEST
"""

import pytest

from django.conf import settings
from django.urls import reverse

import django.core.mail

from pytest_django.asserts import assertRedirects


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


# eof
