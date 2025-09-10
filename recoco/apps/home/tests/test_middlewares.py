from unittest.mock import Mock

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from model_bakery import baker
from pytest_django.asserts import assertRedirects

from recoco.apps.home.middlewares import CurrentSiteConfigurationMiddleware
from recoco.apps.home.models import SiteConfiguration
from recoco.utils import login


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
class TestRedirectIncompleteProfileUserMiddleware:
    def test_does_not_redirect_unauthenticated_users(self, client):
        url = reverse("home")
        response = client.get(url, headers={"accept": "text/html"})
        assert response.status_code == 200

    def test_does_not_loop_redirect(self, client, std_user):
        incomplete_user = std_user
        incomplete_user.profile.needs_profile_update = True
        incomplete_user.profile.save()
        with login(client, user=incomplete_user):
            url = reverse("home-update-incomplete-profile")
            response = client.get(url, headers={"accept": "text/html"})
            assert response.status_code == 200

    def test_does_not_redirect_full_user(self, client, std_user):
        with login(client, user=std_user):
            url = reverse("home")
            response = client.get(url, headers={"accept": "text/html"})
            assert response.status_code == 200

    def test_does_not_redirect_xhr_requests(self, client, std_user):
        incomplete_user = std_user
        incomplete_user.profile.needs_profile_update = True
        incomplete_user.profile.save()
        with login(client, user=incomplete_user):
            url = reverse("home")
            response = client.get(url, headers={"accept": "*/*"})
            assert response.status_code == 200

    def test_redirects_incomplete_users(self, client, std_user):
        incomplete_user = std_user
        incomplete_user.profile.needs_profile_update = True
        incomplete_user.profile.save()
        with login(client, user=incomplete_user):
            url = reverse("home")
            response = client.get(url, headers={"accept": "text/html"})
            assert response.status_code == 302
            assertRedirects(response, reverse("home-update-incomplete-profile"))


# - if XHR call to not redirect

# eof
