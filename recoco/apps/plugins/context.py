from contextlib import contextmanager

from django.conf import settings

from .resolvers import get_enabled_plugins, set_enabled_plugins


@contextmanager
def tenant_plugins_context(site_config):
    """Scope the enabled-plugins registry to a tenant (a SiteConfiguration,
    or None for a site without one).

    While the context is active, ``get_enabled_plugins()`` reflects the
    tenant's ``enabled_plugins``, so plugin hooks and URLs resolve for that
    tenant. The previous registry is restored on exit, so contexts nest.

    The search_path is not touched: plugin schemas are on every connection's
    search_path (see ``set_plugin_search_path``) and plugin rows are scoped by
    ``site``.

    Outside a request, use ``tenant_context`` instead: it also sets SITE_ID.
    """
    previous = get_enabled_plugins()
    enabled_plugins = site_config.enabled_plugins if site_config else None
    set_enabled_plugins(enabled_plugins or [])
    try:
        yield
    finally:
        set_enabled_plugins(previous)


@contextmanager
def tenant_context(site):
    """Act as a tenant outside a request (management commands, tasks, shell).

    Sets both SITE_ID (``on_site`` managers, current site) and the tenant's
    enabled plugins (plugin hooks, URLs), which a request gets from its
    middlewares. Setting only one of them mixes two tenants.
    """
    from .manager import get_site_configuration

    with (
        settings.SITE_ID.override(site.pk),
        tenant_plugins_context(get_site_configuration(site)),
    ):
        yield
