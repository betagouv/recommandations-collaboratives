from contextlib import contextmanager
from typing import Optional

from django.db import connection
from psycopg.sql import SQL, Identifier

from recoco.apps.home.models import SiteConfiguration

from .resolvers import set_enabled_plugins


@contextmanager
def tenant_schema_context(site_config: Optional[SiteConfiguration]):
    """Scope the DB search_path and enabled-plugins registry to a tenant.

    While the context is active, the PostgreSQL search_path is set to
    ``<schema_name>, public`` and ``get_enabled_plugins()`` reflects the
    tenant's ``enabled_plugins``, so plugin hooks and models resolve against
    the right schema. Restores ``search_path`` to ``public`` and clears the
    enabled-plugins registry on exit.

    No-ops (but still clears the enabled-plugins registry) if site_config is
    None or has no schema_name, matching TenantPluginSchemaMiddleware's
    behaviour for tenants without a dedicated schema.
    """
    if not site_config or not site_config.schema_name:
        set_enabled_plugins([])
        yield
        return

    schema = site_config.schema_name
    set_enabled_plugins(site_config.enabled_plugins or [])
    with connection.cursor() as cursor:
        cursor.execute(SQL("SET search_path TO {}, public").format(Identifier(schema)))

    try:
        yield
    finally:
        set_enabled_plugins([])
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO public")
