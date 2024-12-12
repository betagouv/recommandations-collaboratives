from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.backends.utils import CursorWrapper

from recoco.apps.metrics.processor import (
    MaterializedView,
    MaterializedViewSpecError,
)


class Command(BaseCommand):
    help = "Update materialized view used for metrics"

    def _check_user_exists_in_db(self, cursor: CursorWrapper, schema_owner: str):
        cursor.execute(
            sql=f"SELECT 1 FROM pg_roles WHERE rolname='{schema_owner}';"  # noqa: S608
        )
        return cursor.fetchone() is not None

    def create_views(self, **options: Any):
        for spec in settings.METRICS_MATERIALIZED_VIEWS_SPEC:
            try:
                materialized_view = MaterializedView.from_spec(spec=spec)
            except MaterializedViewSpecError as err:
                self.stdout.write(self.style.ERROR(str(err)))
                continue

            with connection.cursor() as cursor:
                materialized_view.set_cursor(cursor)

                if not options["refresh_only"]:
                    for site in Site.objects.order_by("id"):
                        self.stdout.write(
                            f"  >> Dropping materialized view '{materialized_view.site_db_schema_name(site)}.{materialized_view.db_view_name}'"
                        )
                        materialized_view.drop_for_site(site=site)

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

                    for site in Site.objects.order_by("id"):
                        self.stdout.write(
                            f"  >> Refreshing materialized view '{materialized_view.site_db_schema_name(site)}.{materialized_view.db_view_name}'"
                        )
                        materialized_view.create_for_site(site=site)
                        materialized_view.refresh_for_site(site=site)

                if not options["drop_only"] and not options["refresh_only"]:
                    if not self._check_user_exists_in_db(
                        cursor, materialized_view.db_schema_owner
                    ):
                        self.stdout.write(
                            self.style.ERROR(
                                f"  -- User '{materialized_view.db_schema_owner}' does not exist in the database"
                            )
                        )
                    else:
                        self.stdout.write(
                            f"  ++ Assigning permissions to '{materialized_view.db_schema_owner}' on schema '{materialized_view.db_schema_name}'"
                        )
                        materialized_view.assign_permissions()

                    for site in Site.objects.order_by("id"):
                        site_schema_owner = materialized_view.site_db_schema_owner(site)

                        if not self._check_user_exists_in_db(cursor, site_schema_owner):
                            self.stdout.write(
                                self.style.ERROR(
                                    f"  -- User '{site_schema_owner}' does not exist in the database"
                                )
                            )
                        else:
                            self.stdout.write(
                                f"  ++ Assigning permissions to '{site_schema_owner}' on schema '{materialized_view.site_db_schema_name(site)}'"
                            )
                            materialized_view.assign_permissions_for_site(site=site)

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
                    "You can't use both --drop-only and --refresh-only at the same time"
                )
            )
            return

        self.create_views(**options)
