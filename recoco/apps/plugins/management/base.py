from django.core.management.base import BaseCommand, CommandError

from recoco.apps.home.models import SiteConfiguration
from recoco.apps.plugins.manager import get_site_plugin_manager
from recoco.apps.plugins.schema import tenant_schema_context


class TenantCommand(BaseCommand):
    """Base class for management commands that operate on a tenant schema.

    Sets the PostgreSQL search_path to ``<schema>, public`` before handle()
    is called, so all ORM queries against plugin models resolve to the correct
    tenant schema.

    By default, the schema is taken from the --schema argument. Override
    get_schema(options) to derive it from other arguments (e.g. --site-domain).

    The resolved SiteConfiguration is stored as ``self.site_config`` for use
    in handle(). Use ``self.plugin_manager`` to get a plugin manager scoped to
    that site.
    """

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--schema", required=False, help="PostgreSQL schema name")

    def get_schema(self, options):
        schema = options.get("schema")
        if not schema:
            raise CommandError(
                "No schema provided. Pass --schema or override get_schema()."
            )
        return schema

    @property
    def plugin_manager(self):
        return get_site_plugin_manager(self.site_config.site)

    def execute(self, *args, **options):
        schema = self.get_schema(options)

        try:
            site_config = SiteConfiguration.objects.get(schema_name=schema)
        except SiteConfiguration.DoesNotExist as err:
            raise CommandError(
                f"No SiteConfiguration found for schema '{schema}'"
            ) from err

        self.site_config = site_config

        # Mirror what TenantPluginSchemaMiddleware does for HTTP requests so
        # that PluginURLResolver.reverse() works inside management commands.
        with tenant_schema_context(site_config):
            super().execute(*args, **options)
