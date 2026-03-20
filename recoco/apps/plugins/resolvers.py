import threading

from django.urls import NoReverseMatch, Resolver404
from django.urls.resolvers import RoutePattern, URLResolver

# Thread-local storage for the current request's enabled plugins
_state = threading.local()


def set_enabled_plugins(plugins: list[str]) -> None:
    _state.enabled_plugins = plugins


def get_enabled_plugins() -> list[str]:
    return getattr(_state, "enabled_plugins", [])


class PluginURLResolver(URLResolver):
    """
    A URLResolver that only resolves if the named plugin
    is in the current tenant's enabled_plugins list.
    """

    def __init__(self, plugin_name: str, prefix: str, urlconf):
        self.plugin_name = plugin_name
        super().__init__(RoutePattern(prefix), urlconf)

    def resolve(self, path):
        if self.plugin_name not in get_enabled_plugins():
            raise Resolver404({"tried": [], "path": path})
        return super().resolve(path)

    def _reverse_with_prefix(self, lookup_view, _prefix, *args, **kwargs):
        if self.plugin_name not in get_enabled_plugins():
            raise NoReverseMatch(
                f"Plugin '{self.plugin_name}' is not enabled for this tenant."
            )
        return super()._reverse_with_prefix(lookup_view, _prefix, *args, **kwargs)
