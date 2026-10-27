import pytest
from django.conf import settings
from django.contrib.sites.models import Site
from model_bakery import baker

from recoco.apps.home.models import SiteConfiguration

from .context import tenant_context, tenant_plugins_context
from .resolvers import get_enabled_plugins, set_enabled_plugins


class FakeSiteConfig:
    def __init__(self, enabled_plugins):
        self.enabled_plugins = enabled_plugins


@pytest.fixture(autouse=True)
def reset_enabled_plugins():
    yield
    set_enabled_plugins([])


def test_tenant_plugins_context_restores_previous_plugins():
    set_enabled_plugins(["plugin_outer"])

    with tenant_plugins_context(FakeSiteConfig(["plugin_inner"])):
        assert get_enabled_plugins() == ["plugin_inner"]

    assert get_enabled_plugins() == ["plugin_outer"]


def test_tenant_plugins_contexts_nest():
    with tenant_plugins_context(FakeSiteConfig(["plugin_a"])):
        with tenant_plugins_context(None):
            assert get_enabled_plugins() == []
        assert get_enabled_plugins() == ["plugin_a"]
    assert get_enabled_plugins() == []


def test_tenant_plugins_context_restores_on_error():
    with pytest.raises(RuntimeError):
        with tenant_plugins_context(FakeSiteConfig(["plugin_a"])):
            raise RuntimeError

    assert get_enabled_plugins() == []


@pytest.mark.django_db
def test_tenant_context_sets_site_and_plugins(current_site):
    other_site = baker.make(Site, domain="other.example.com")
    baker.make(SiteConfiguration, site=other_site, enabled_plugins=["plugin_a"])

    with tenant_context(other_site):
        assert Site.objects.get_current() == other_site
        assert get_enabled_plugins() == ["plugin_a"]

    assert settings.SITE_ID == current_site.pk
    assert get_enabled_plugins() == []


@pytest.mark.django_db
def test_tenant_context_without_site_configuration(current_site):
    other_site = baker.make(Site, domain="other.example.com")

    with tenant_context(other_site):
        assert Site.objects.get_current() == other_site
        assert get_enabled_plugins() == []
