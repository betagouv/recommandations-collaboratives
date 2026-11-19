import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from recoco.apps.home.throttling import UserButExceptionThrottle
from recoco.utils import get_group_for_site


@pytest.fixture
def low_throttle_rate(monkeypatch):
    cache.clear()
    monkeypatch.setattr(
        UserButExceptionThrottle,
        "THROTTLE_RATES",
        {"anon": "100/day", "user_but_exception": "2/day"},
    )
    yield
    cache.clear()


def call_api(user, times):
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("notifications-mark-all-as-read")
    return [client.patch(url).status_code for _ in range(times)]


@pytest.mark.django_db
def test_regular_user_is_throttled(low_throttle_rate):
    user = baker.make(auth_models.User)
    assert call_api(user, 3) == [200, 200, 429]


@pytest.mark.django_db
def test_trusted_bot_is_not_throttled(current_site, low_throttle_rate):
    bot = baker.make(auth_models.User)
    get_group_for_site("trusted_bot", current_site).user_set.add(bot)
    assert call_api(bot, 5) == [200] * 5


@pytest.mark.django_db
def test_trusted_bot_of_other_site_is_not_throttled_either(low_throttle_rate):
    other_site = baker.make(Site)
    bot = baker.make(auth_models.User)
    get_group_for_site("trusted_bot", other_site, create=True).user_set.add(bot)
    assert call_api(bot, 5) == [200] * 5
