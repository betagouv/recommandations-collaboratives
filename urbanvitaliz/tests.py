from django.contrib.auth import models as auth
from model_bakery.recipe import Recipe

from . import utils


def test_build_absolute_url():
    url = utils.build_absolute_url("somewhere")

    assert url.startswith("https://")
    assert "/somewhere" in url
    assert "?sesame=" not in url


def test_build_absolute_url_with_auto_login():
    user = Recipe(auth.User, username="owner", email="owner@example.com").make()

    url = utils.build_absolute_url("somewhere", user)

    assert url.startswith("https://")
    assert "/somewhere" in url
    assert "?sesame=" in url


def test_build_absolute_url_with_empty_auto_login():
    url = utils.build_absolute_url("somewhere", auto_login_user=None)

    assert url.startswith("https://")
    assert "/somewhere" in url
    assert "?sesame=" not in url
