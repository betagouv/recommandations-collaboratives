from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from psycopg.sql import SQL, Identifier

from recoco.apps.home.models import SiteConfiguration
from recoco.apps.plugins.routers import TenantPluginRouter


class Command(BaseCommand):
    help = "Run plugin migrations for a specific tenant schema"

    def add_arguments(self, parser):
        parser.add_argument("--schema", required=True, help="PostgreSQL schema name")
        parser.add_argument(
            "app_label", nargs="?", help="Optional app label to migrate"
        )
        parser.add_argument(
            "migration_name", nargs="?", help="Optional migration name to migrate to"
        )

    def handle(self, *args, **options):
        schema = options["schema"]
        app_label = options["app_label"]
        migration_name = options["migration_name"]

        try:
            site_config = SiteConfiguration.objects.get(schema_name=schema)
        except SiteConfiguration.DoesNotExist as err:
            raise CommandError(
                f"No SiteConfiguration found for schema '{schema}'"
            ) from err

        # Verify the PostgreSQL schema exists before proceeding.
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
                [schema],
            )
            if not cursor.fetchone():
                raise CommandError(
                    f"Schema '{schema}' does not exist in the database. "
                    "It is created automatically by the post_save signal on "
                    "SiteConfiguration when plugins are first enabled."
                )

        # If app_label is given, use it directly (same syntax as `migrate`).
        # Otherwise migrate all plugins enabled for this tenant.
        if app_label:
            plugins_to_migrate = [(app_label, migration_name)]
        else:
            enabled_plugins = site_config.enabled_plugins or []
            if not enabled_plugins:
                self.stdout.write(
                    f"No plugins enabled for schema '{schema}', nothing to do."
                )
                return
            plugins_to_migrate = [(app, None) for app in enabled_plugins]

        self.stdout.write(f"Migrating schema '{schema}'...")

        try:
            TenantPluginRouter.is_tenant_operation = True

            # Point at the tenant schema so ensure_schema() creates
            # django_migrations there rather than reusing public's.
            with connection.cursor() as cursor:
                cursor.execute(SQL("SET search_path TO {}").format(Identifier(schema)))

            MigrationRecorder(connection).ensure_schema()

            # Pre-populate the tenant's django_migrations with every core migration
            # already applied in public.  Django reads this table to build the
            # migration plan and project state. Without these entries it would try
            # to re-execute all core migrations here (they would be no-ops thanks to
            # the router, but it is slow and produces noisy output).
            #
            # We INSERT but never DELETE: a ghost entry for a core migration that
            # was later rolled back in public is semantically correc. It means
            # "don't re-apply this here", which is true regardless of public's state,
            # because the tenant never ran that SQL in the first place.
            # See docs/plugins.rst for more details on that.
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL("""
                    INSERT INTO {dm} (app, name, applied)
                    SELECT app, name, applied
                    FROM public.django_migrations
                    WHERE app NOT LIKE 'plugin_%%'
                      AND NOT EXISTS (
                        SELECT 1 FROM {dm} existing
                        WHERE existing.app = public.django_migrations.app
                          AND existing.name = public.django_migrations.name
                      )
                    """).format(dm=Identifier(schema, "django_migrations"))
                )
                cursor.execute(
                    SQL("SET search_path TO {}, public").format(Identifier(schema))
                )

            for plugin_app, target in plugins_to_migrate:
                self.stdout.write(f"  Applying migrations for '{plugin_app}'...")
                migrate_args = [plugin_app]
                if target:
                    migrate_args.append(target)
                call_command("migrate", *migrate_args, verbosity=options["verbosity"])

        finally:
            TenantPluginRouter.is_tenant_operation = False
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully migrated schema '{schema}'")
        )
