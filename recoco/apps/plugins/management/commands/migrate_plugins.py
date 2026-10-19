from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from psycopg.sql import SQL, Identifier

from recoco.apps.plugins.routers import TenantPluginRouter
from recoco.apps.plugins.utils import get_plugin_app_labels


class Command(BaseCommand):
    help = (
        "Run plugin migrations, each plugin in its own PostgreSQL schema "
        "(named after the plugin app label)"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "app_label", nargs="?", help="Optional plugin app label to migrate"
        )
        parser.add_argument(
            "migration_name", nargs="?", help="Optional migration name to migrate to"
        )

    def handle(self, *args, **options):
        app_label = options["app_label"]
        migration_name = options["migration_name"]
        installed_plugins = get_plugin_app_labels()

        # If app_label is given, use it directly (same syntax as `migrate`).
        # Otherwise migrate every installed plugin, enabled for a site or not.
        if app_label:
            if app_label not in installed_plugins:
                raise CommandError(f"'{app_label}' is not an installed plugin app")
            plugins_to_migrate = [(app_label, migration_name)]
        else:
            if not installed_plugins:
                self.stdout.write("No plugin installed, nothing to do.")
                return
            plugins_to_migrate = [(app, None) for app in installed_plugins]

        for plugin_app, target in plugins_to_migrate:
            self.migrate_plugin(plugin_app, target, options["verbosity"])

    def migrate_plugin(self, plugin_app, target, verbosity):
        schema = plugin_app
        self.stdout.write(f"Migrating '{plugin_app}' in schema '{schema}'...")

        try:
            TenantPluginRouter.is_plugin_operation = True

            # Point at the plugin schema only so ensure_schema() creates
            # django_migrations there rather than reusing public's.
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL("CREATE SCHEMA IF NOT EXISTS {}").format(Identifier(schema))
                )
                cursor.execute(SQL("SET search_path TO {}").format(Identifier(schema)))

            MigrationRecorder(connection).ensure_schema()

            # Pre-populate the plugin's django_migrations with every core migration
            # already applied in public.  Django reads this table to build the
            # migration plan and project state. Without these entries it would try
            # to re-execute all core migrations here (they would be no-ops thanks to
            # the router, but it is slow and produces noisy output).
            #
            # A separate django_migrations per plugin schema is required: a plain
            # `migrate` records router-skipped plugin migrations as applied in
            # public.django_migrations, without creating any table.
            #
            # We INSERT but never DELETE: a ghost entry for a core migration that
            # was later rolled back in public is semantically correct. It means
            # "don't re-apply this here", which is true regardless of public's state,
            # because the plugin schema never ran that SQL in the first place.
            # See docs/plugins.rst for more details on that.
            with connection.cursor() as cursor:
                cursor.execute(
                    SQL("""
                    INSERT INTO {dm} (app, name, applied)
                    SELECT app, name, applied
                    FROM public.django_migrations
                    WHERE app NOT LIKE 'plugin\\_%%'
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

            migrate_args = [plugin_app]
            if target:
                migrate_args.append(target)
            call_command("migrate", *migrate_args, verbosity=verbosity)

        finally:
            TenantPluginRouter.is_plugin_operation = False
            with connection.cursor() as cursor:
                cursor.execute("RESET search_path")

        self.stdout.write(self.style.SUCCESS(f"Successfully migrated '{plugin_app}'"))
