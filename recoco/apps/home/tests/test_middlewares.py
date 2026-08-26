from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from model_bakery import baker
from sesame.utils import get_query_string

from conftest import setup_sesame_cookie
from recoco.apps.home.middlewares import CurrentSiteConfigurationMiddleware
from recoco.apps.home.models import SiteConfiguration
from recoco.utils import check_email_verified, login


@pytest.fixture
def get_response_mock():
    return Mock()


@pytest.fixture
def middleware(get_response_mock):
    return CurrentSiteConfigurationMiddleware(get_response=get_response_mock)


@pytest.fixture
def request_mock():
    return Mock()


@pytest.mark.django_db
class TestCurrentSiteConfigurationMiddleware:
    def test_raises_error_if_request_has_no_site_attribute(
        self, middleware, request_mock
    ):
        delattr(request_mock, "site")  # Ensure the 'site' attribute is missing

        with pytest.raises(
            ImproperlyConfigured,
            match="The request object does not have a 'site' attribute",
        ):
            middleware(request_mock)

    def test_sets_site_config_on_request(self, middleware, request_mock, current_site):
        site_config = baker.make(SiteConfiguration, site=current_site)

        request_mock.site = current_site
        middleware(request_mock)

        assert request_mock.site_config == site_config


@pytest.mark.django_db
class TestSesameWithCookie:
    def test_login_fails_if_no_cookie(self, client):
        user = baker.make(auth_models.User)
        query = get_query_string(user)

        url = reverse("home") + query
        response = client.get(url)

        authenticated_user = get_user(client)
        assert authenticated_user.is_anonymous
        assert response.status_code != 302
        assert not check_email_verified(user)

    def test_login_fails_with_other_cookie(self, client):
        user = baker.make(auth_models.User)
        setup_sesame_cookie(client, baker.make(auth_models.User))

        query = get_query_string(user)
        url = reverse("home") + query
        response = client.get(url)

        authenticated_user = get_user(client)
        assert authenticated_user.is_anonymous
        assert response.status_code != 302
        assert not check_email_verified(user)

    def test_succeeds_with_proper_cookie(self, client):
        user = baker.make(auth_models.User)
        setup_sesame_cookie(client, user)

        query = get_query_string(user)
        url = reverse("home") + query
        response = client.get(url)

        authenticated_user = get_user(client)
        assert authenticated_user.id == user.id
        assert response.status_code == 302

    def test_does_not_logout_even_if_cookie(self, client):
        user = baker.make(auth_models.User)
        setup_sesame_cookie(client, user)
        query = get_query_string(user)

        with login(client) as other_user:
            url = reverse("home") + query
            response = client.get(url)

            authenticated_user = get_user(client)
            assert authenticated_user.id == other_user.id
            assert response.status_code == 200
        assert not check_email_verified(user)

    def test_sesame_login_confirms_email(self, client):
        user = baker.make(auth_models.User)
        setup_sesame_cookie(client, user)
        assert not check_email_verified(user)

        url = reverse("home") + get_query_string(user)
        client.get(url)

        assert check_email_verified(user)


@pytest.mark.django_db
class TestEnableSesameCookie:
    def test_sets_cookie_if_consent(self, client):
        cookie_url = reverse("cookie_consent_accept_all")
        client.post(cookie_url)

        with login(client) as user:
            client.get("/")
            assert int(client.cookies["enable-sesame-user-id"].value) == user.id

    def test_persist_after_session(self, client):
        cookie_url = reverse("cookie_consent_accept_all")
        client.post(cookie_url)

        with login(client) as user:
            client.get("/")
            assert int(client.cookies["enable-sesame-user-id"].value) == user.id
            client.get(reverse("account_logout"))
            assert int(client.cookies["enable-sesame-user-id"].value) == user.id

    def test_no_cookie_if_hijacked(self, client):
        hijacked = baker.make(auth_models.User, username="hijacked")
        cookie_url = reverse("cookie_consent_accept_all")
        client.post(cookie_url)

        with login(client, username="hijacker", is_staff=True):
            url = reverse("hijack:acquire")
            client.post(url, data={"user_pk": hijacked.pk})
            client.get("/")
            assert "enable-sesame-user-id" not in client.cookies

    def test_no_cookie_with_unset_consent(self, client):
        with login(client):
            client.get("/")
            assert "enable-sesame-user-id" not in client.cookies

    def test_no_cookie_without_consent(self, client):
        cookie_url = reverse("cookie_consent_decline_all")
        client.post(cookie_url)

        with login(client):
            client.get("/")
            assert "enable-sesame-user-id" not in client.cookies

    def test_new_cookie_replaces_old_one(self, client):
        old_user = baker.make(auth_models.User)
        client.cookies.load({"enable-sesame-user-id": str(old_user.id)})
        cookie_url = reverse("cookie_consent_accept_all")
        client.post(cookie_url)

        with login(client) as new_user:
            client.get("/")
            assert int(client.cookies["enable-sesame-user-id"].value) == new_user.id


@pytest.mark.django_db
def test_save_previous_activity_data(client, current_site):
    site1 = baker.make(site_models.Site, pk=1)
    user = baker.make(auth_models.User)
    user.profile.previous_activity_at = None
    user.profile.previous_activity_site = site1
    user.profile.save()

    url = reverse("home")
    with login(client, user=user):
        response = client.get(url)
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.profile.previous_activity_at is not None
        assert user.profile.previous_activity_site == current_site


@pytest.mark.django_db
def test_dont_save_previous_activity_data_if_hijacked(client, rf, current_site):
    site1 = baker.make(site_models.Site, pk=1)
    last_date = datetime(2012, 12, 12, tzinfo=timezone.utc)
    hijacked = baker.make(auth_models.User)
    hijacked.profile.previous_activity_at = last_date
    hijacked.profile.previous_activity_site = site1
    hijacked.profile.save()

    with login(client, username="hijacker", is_staff=True):
        hijacked.refresh_from_db()
        url = reverse("hijack:acquire")
        client.post(url, data={"user_pk": hijacked.pk})
        hijacked.refresh_from_db()

        url = reverse("home")
        response = client.get(url)

        assert response.status_code == 200
        hijacked.refresh_from_db()
        assert hijacked.profile.previous_activity_at == last_date
        assert hijacked.profile.previous_activity_site == site1
