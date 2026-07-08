from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from psycopg.sql import SQL, Identifier

from recoco.apps.home.models import SiteConfiguration
from recoco.apps.plugins.resolvers import set_enabled_plugins


class TenantCommand(BaseCommand):
    """Base class for management commands that operate on a tenant schema.

    Sets the PostgreSQL search_path to ``<schema>, public`` before handle()
    is called, so all ORM queries against plugin models resolve to the correct
    tenant schema.

    By default, the schema is taken from the --schema argument. Override
    get_schema(options) to derive it from other arguments (e.g. --site-domain).
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

    def execute(self, *args, **options):
        schema = self.get_schema(options)

        try:
            site_config = SiteConfiguration.objects.get(schema_name=schema)
        except SiteConfiguration.DoesNotExist as err:
            raise CommandError(
                f"No SiteConfiguration found for schema '{schema}'"
            ) from err

        with connection.cursor() as cursor:
            cursor.execute(
                SQL("SET search_path TO {}, public").format(Identifier(schema))
            )

        # Mirror what TenantPluginSchemaMiddleware does for HTTP requests so
        # that PluginURLResolver.reverse() works inside management commands.
        set_enabled_plugins(site_config.enabled_plugins or [])

        super().execute(*args, **options)
