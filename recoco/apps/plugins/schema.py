from contextlib import contextmanager
from typing import Optional

from recoco.apps.home.models import SiteConfiguration

from .resolvers import set_enabled_plugins


@contextmanager
def tenant_schema_context(site_config: Optional[SiteConfiguration]):
    """Scope the enabled-plugins registry to a tenant.

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
