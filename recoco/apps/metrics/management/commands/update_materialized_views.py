from string import Template
from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.backends.utils import CursorWrapper

from recoco.apps.metrics.processor import (
    MaterializedView,
    MaterializedViewSpecError,
)
from recoco.utils import make_site_slug


class Command(BaseCommand):
    help = "Update materialized view used for metrics"

    def _check_user_exists_in_db(self, cursor: CursorWrapper, schema_owner: str):
        cursor.execute(
            sql=f"SELECT 1 FROM pg_roles WHERE rolname='{schema_owner}';"  # noqa: S608
        )
        return cursor.fetchone() is not None

    def _assign_permissions_to_owner(
        self, cursor: CursorWrapper, schema_name: str, schema_owner: str
    ):
        cursor.execute(
            sql=f"GRANT CONNECT ON DATABASE {connection.settings_dict['NAME']} TO {schema_owner};"
        )
        cursor.execute(sql=f"GRANT USAGE ON SCHEMA {schema_name} TO {schema_owner};")

        cursor.execute(
            sql=f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema_name} TO {schema_owner};"
        )

    def _create_views_for_site(self, site: Site, **options: Any):
        self.stdout.write(
            f"Updating materialized views for site {site.name} (#{site.id})"
        )

        with connection.cursor() as cursor:
            with transaction.atomic():
                for spec in settings.METRICS_MATERIALIZED_VIEWS_SPEC:
                    try:
                        materialized_view = MaterializedView.create_for_site(
                            site=site, spec=spec
                        )
                    except MaterializedViewSpecError as err:
                        self.stdout.write(self.style.ERROR(str(err)))
                        continue

                    materialized_view.set_cursor(cursor)

                    if not options["refresh_only"]:
                        self.stdout.write(
                            f"  >> Dropping materialized view '{materialized_view.db_schema_name}.{materialized_view.db_view_name}'"
                        )
                        materialized_view.drop()

                    if not options["drop_only"]:
                        self.stdout.write(
                            f"  >> Refreshing materialized view '{materialized_view.db_schema_name}.{materialized_view.db_view_name}'"
                        )
                        materialized_view.create()
                        materialized_view.refresh()

                # if an owner is specified, assign rights
                if (
                    settings.METRICS_MATERIALIZED_VIEWS_OWNER_TPL
                    and not options["drop_only"]
                ):
                    db_schema_name = MaterializedView.make_db_schema_name(site)

                    # Check first if we have an owner override
                    schema_owner = (
                        settings.METRICS_MATERIALIZED_VIEWS_OWNER_OVERRIDES.get(
                            make_site_slug(site), None
                        )
                    )

                    # Compute default one in case we didn't find an override
                    if not schema_owner:
                        schema_owner = Template(
                            settings.METRICS_MATERIALIZED_VIEWS_OWNER_TPL
                        ).substitute(
                            site_name=site.name,
                            site_slug=make_site_slug(site=site),
                        )

                    if not self._check_user_exists_in_db(cursor, schema_owner):
                        self.stdout.write(
                            self.style.ERROR(
                                f"  -- Owner '{schema_owner}' does not exist in the database"
                            )
                        )
                        return

                    self.stdout.write(
                        f"  ++ Assigning permissions to '{schema_owner}' on schema '{db_schema_name}'"
                    )

                    self._assign_permissions_to_owner(
                        cursor=cursor,
                        schema_name=db_schema_name,
                        schema_owner=schema_owner,
                    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--drop-only",
            action="store_true",
            help="Drop the materialized views only, do not recreate them.",
        )
        parser.add_argument(
            "--refresh-only",
            action="store_true",
            help="Refresh the materialized views only, do not drop them.",
        )

    def handle(self, *args, **options):
        if options["drop_only"] and options["refresh_only"]:
            self.stdout.write(
                self.style.ERROR(
                    "Cannot use both --drop-only and --refresh-only at the same time"
                )
            )
            return

        for site in Site.objects.order_by("id"):
            with settings.SITE_ID.override(site.pk):
                self._create_views_for_site(site, **options)
