import pluggy
import pytest
from django.http import HttpResponse
from django.urls import NoReverseMatch, Resolver404, path

from recoco.apps.home.models import SiteConfiguration
from recoco.rest_api.urls import _collect_plugin_rest_urls

from .context import tenant_plugins_context
from .resolvers import PluginURLResolver
from .testing import PLUGIN

PATH = "plugin-testapp/ping/"

# This module doubles as the plugin's REST urls module
urlpatterns = [
    path(PATH, lambda request: HttpResponse("pong"), name="plugin-testapp-ping"),
]


class FakeRestPlugin:
    rest_urls_module = __name__


@pytest.fixture
def plugin_rest_urls():
    pm = pluggy.PluginManager("recoco")
    pm.register(FakeRestPlugin(), name=PLUGIN)
    return _collect_plugin_rest_urls(pm)


def test_plugin_rest_urls_are_wrapped_in_plugin_resolver(plugin_rest_urls):
    [resolver] = plugin_rest_urls
    assert isinstance(resolver, PluginURLResolver)
    assert resolver.plugin_name == PLUGIN
    # No namespace added, url names stay global
    assert resolver.namespace is None


def test_plugin_rest_url_only_resolves_and_reverses_where_plugin_enabled(
    plugin_rest_urls,
):
    # Built once at startup and shared by every tenant: nothing may stick
    # from one tenant to the next.
    [resolver] = plugin_rest_urls
    for enabled_plugins in ([PLUGIN], [], [PLUGIN], ["plugin_other"]):
        with tenant_plugins_context(SiteConfiguration(enabled_plugins=enabled_plugins)):
            if PLUGIN in enabled_plugins:
                assert resolver.resolve(PATH).url_name == "plugin-testapp-ping"
                assert resolver.reverse("plugin-testapp-ping") == PATH
            else:
                with pytest.raises(Resolver404):
                    resolver.resolve(PATH)
                with pytest.raises(NoReverseMatch):
                    resolver.reverse("plugin-testapp-ping")


def test_plugin_without_rest_urls_module_is_skipped():
    pm = pluggy.PluginManager("recoco")
    pm.register(object(), name=PLUGIN)
    assert _collect_plugin_rest_urls(pm) == []
