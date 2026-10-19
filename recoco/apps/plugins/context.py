from contextlib import contextmanager

from .resolvers import set_enabled_plugins


@contextmanager
def tenant_plugins_context(site_config):
    """Scope the enabled-plugins registry to a tenant (a SiteConfiguration,
    or None for a site without one).

    While the context is active, ``get_enabled_plugins()`` reflects the
    tenant's ``enabled_plugins``, so plugin hooks and URLs resolve for that
    tenant. The registry is cleared on exit.

    The search_path is not touched: plugin schemas are on every connection's
    search_path (see ``set_plugin_search_path``) and plugin rows are scoped by
    ``site``.
    """
    enabled_plugins = site_config.enabled_plugins if site_config else None
    set_enabled_plugins(enabled_plugins or [])
    try:
        yield
    finally:
        set_enabled_plugins([])
