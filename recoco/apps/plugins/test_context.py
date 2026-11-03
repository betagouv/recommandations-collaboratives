import threading

import pytest
from django.conf import settings
from django.contrib.sites.models import Site
from model_bakery import baker

from recoco.apps.home.models import SiteConfiguration

from .context import tenant_context, tenant_plugins_context
from .resolvers import get_enabled_plugins


def test_tenant_plugins_contexts_nest(enabled_plugins):
    with tenant_plugins_context(SiteConfiguration(enabled_plugins=["plugin_a"])):
        with tenant_plugins_context(None):
            assert get_enabled_plugins() == []
        assert get_enabled_plugins() == ["plugin_a"]
    assert get_enabled_plugins() == []


def test_tenant_plugins_context_restores_on_error(enabled_plugins):
    with pytest.raises(RuntimeError):
        with tenant_plugins_context(SiteConfiguration(enabled_plugins=["plugin_a"])):
            raise RuntimeError

    assert get_enabled_plugins() == []


def test_enabled_plugins_are_per_thread(enabled_plugins):
    # Resolvers are shared by every request: tenants on other threads must
    # not see each other's plugins
    seen = []
    enabled_plugins("plugin_a")

    thread = threading.Thread(target=lambda: seen.append(get_enabled_plugins()))
    thread.start()
    thread.join()

    assert seen == [[]]


@pytest.mark.django_db
def test_tenant_context_sets_site_and_plugins(current_site):
    other_site = baker.make(Site, domain="other.example.com")
    baker.make(SiteConfiguration, site=other_site, enabled_plugins=["plugin_a"])

    with tenant_context(other_site):
        assert Site.objects.get_current() == other_site
        assert get_enabled_plugins() == ["plugin_a"]

    assert settings.SITE_ID == current_site.pk
    assert get_enabled_plugins() == []
