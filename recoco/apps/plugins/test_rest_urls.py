import threading

import pluggy
import pytest
from django.urls import Resolver404

from recoco.rest_api.urls import _collect_plugin_rest_urls

from .context import tenant_plugins_context
from .resolvers import PluginURLResolver

PLUGIN = "plugin_testapp"
PATH = "plugin-testapp/ping/"


class FakeRestPlugin:
    rest_urls_module = "recoco.apps.plugins.testing.plugin_testapp.rest_urls"


class FakeSiteConfig:
    def __init__(self, enabled_plugins):
        self.enabled_plugins = enabled_plugins


@pytest.fixture
def plugin_rest_urls():
    pm = pluggy.PluginManager("recoco")
    pm.register(FakeRestPlugin(), name=PLUGIN)
    return _collect_plugin_rest_urls(pm)


def test_plugin_rest_urls_are_wrapped_in_plugin_resolver(plugin_rest_urls):
    assert len(plugin_rest_urls) == 1
    resolver = plugin_rest_urls[0]
    assert isinstance(resolver, PluginURLResolver)
    assert resolver.plugin_name == PLUGIN
    # No namespace added, url names stay global
    assert resolver.namespace is None


def test_plugin_rest_url_resolves_when_plugin_enabled(plugin_rest_urls):
    with tenant_plugins_context(FakeSiteConfig([PLUGIN])):
        match = plugin_rest_urls[0].resolve(PATH)
    assert match.url_name == "plugin-testapp-ping"


@pytest.mark.parametrize("enabled_plugins", [[], ["plugin_other"]])
def test_plugin_rest_url_does_not_resolve_when_plugin_disabled(
    plugin_rest_urls, enabled_plugins
):
    with tenant_plugins_context(FakeSiteConfig(enabled_plugins)):
        with pytest.raises(Resolver404):
            plugin_rest_urls[0].resolve(PATH)


def can_resolve(resolver):
    try:
        resolver.resolve(PATH)
    except Resolver404:
        return False
    return True


def test_same_resolver_instance_follows_each_tenant(plugin_rest_urls):
    # Built once at startup and shared by every tenant: nothing may stick
    # from one tenant to the next.
    resolver = plugin_rest_urls[0]
    for enabled_plugins, expected in [
        ([PLUGIN], True),
        ([], False),
        ([PLUGIN], True),
        (["plugin_other"], False),
    ]:
        with tenant_plugins_context(FakeSiteConfig(enabled_plugins)):
            assert can_resolve(resolver) is expected


def test_same_resolver_instance_is_isolated_between_threads(plugin_rest_urls):
    resolver = plugin_rest_urls[0]
    barrier = threading.Barrier(2)
    results = {}

    def run(name, enabled_plugins):
        with tenant_plugins_context(FakeSiteConfig(enabled_plugins)):
            # Both threads have set their tenant before either resolves
            barrier.wait()
            results[name] = [can_resolve(resolver) for _ in range(50)]

    threads = [
        threading.Thread(target=run, args=("enabled", [PLUGIN])),
        threading.Thread(target=run, args=("disabled", [])),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert all(results["enabled"])
    assert not any(results["disabled"])


def test_plugin_without_rest_urls_module_is_skipped():
    pm = pluggy.PluginManager("recoco")
    pm.register(object(), name=PLUGIN)
    assert _collect_plugin_rest_urls(pm) == []
