from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

from recoco.apps.plugins.routers import TenantPluginRouter


class Command(BaseCommand):
    help = "Run migrations for a specific tenant schema"

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

        self.stdout.write(f"Migrating schema '{schema}'...")

        # Enable tenant operations in the router
        TenantPluginRouter.is_tenant_operation = True

        try:
            # Extends the path to the tenant schema
            with connection.cursor() as cursor:
                # XXX: use paramterized query instead
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                cursor.execute(f"SET search_path TO {schema}, public")

                # We need a tenant-local django_migrations table so Django's
                # MigrationRecorder doesn't fall back to public.django_migrations
                # That would prevent a migration from being applyed to multiple tenants
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS django_migrations (
                        id SERIAL PRIMARY KEY,
                        app VARCHAR(255) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied TIMESTAMPTZ NOT NULL
                    )
                """)

            # Now we can call django migrate routine with the added schema
            migrate_args = []
            if app_label:
                migrate_args.append(app_label)
            if migration_name:
                migrate_args.append(migration_name)

            call_command("migrate", *migrate_args, verbosity=options["verbosity"])

        finally:
            # Remove the tenant path extension
            TenantPluginRouter.is_tenant_operation = False
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO public")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully migrated schema '{schema}'")
        )
