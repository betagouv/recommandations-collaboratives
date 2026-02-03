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

from recoco.utils import login


@pytest.mark.django_db
def test_user_login_updates_activity_fields(client, request):
    previous_login = timezone.now()
    user = baker.make(auth_models.User, last_login=previous_login)

    with login(client, user=user) as user:
        assert user.profile.previous_activity_at != user.last_login
        assert user.profile.previous_activity_at.date() == previous_login.date()
        assert user.profile.previous_activity_at == previous_login
        assert user.last_login > previous_login
