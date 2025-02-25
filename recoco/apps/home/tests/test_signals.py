# encoding: utf-8

"""
Tests for survey application

authors: guillaume.libersat@beta.gouv.fr
created: 2024-02-06 10:33:33 CEST
"""

import pytest
from django.contrib.auth import models as auth_models
from django.utils import timezone
from model_bakery import baker

from recoco.apps.home.models import UserLoginEntry
from recoco.utils import login


@pytest.mark.django_db
def test_user_login_updates_login_fields(client, request, current_site):
    previous_login = timezone.now()
    user = baker.make(auth_models.User, last_login=previous_login)

    assert UserLoginEntry.objects.count() == 0

    with login(client, user=user) as user:
        assert user.profile.previous_login_at != user.last_login
        assert user.profile.previous_login_at.date() == previous_login.date()
        assert user.profile.previous_login_at == previous_login
        assert user.last_login > previous_login

        assert UserLoginEntry.objects.count() == 1
        logged_in_entry = UserLoginEntry.objects.first()
        assert logged_in_entry.site == current_site
        assert logged_in_entry.profile == user.profile
        assert logged_in_entry.action == UserLoginEntry.ACTION_LOGGED_IN

        client.logout()

        assert UserLoginEntry.objects.count() == 2
        logged_out_entry = UserLoginEntry.objects.first()
        assert logged_out_entry.site == current_site
        assert logged_out_entry.profile == user.profile
        assert logged_out_entry.action == UserLoginEntry.ACTION_LOGGED_OUT
