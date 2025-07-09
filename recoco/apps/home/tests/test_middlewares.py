from unittest.mock import Mock

import pytest
from django.core.exceptions import ImproperlyConfigured
from model_bakery import baker

from recoco.apps.home.middlewares import CurrentSiteConfigurationMiddleware
from recoco.apps.home.models import SiteConfiguration


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
