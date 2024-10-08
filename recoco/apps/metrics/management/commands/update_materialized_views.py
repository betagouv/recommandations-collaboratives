from string import Template
from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from recoco.apps.metrics.processor import (
    MaterializedView,
    MaterializedViewSpecError,
)
from recoco.utils import make_site_slug


class Command(BaseCommand):
    help = "Update materialized view used for metrics"

    def _assign_permissions_to_owner(self, cursor, schema_name: str, schema_owner: str):
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
                for spec in settings.MATERIALIZED_VIEWS_SPEC:
                    try:
                        materialized_view = MaterializedView.create_for_site(
                            site=site, spec=spec
                        )
                    except MaterializedViewSpecError as err:
                        self.stdout.write(self.style.ERROR(str(err)))
                        continue

                    materialized_view.set_cursor(cursor)

                    self.stdout.write(
                        f"  >> Refreshing materialized view '{materialized_view.db_schema_name}.{materialized_view.db_view_name}'"
                    )
                    materialized_view.create()
                    materialized_view.refresh()

                # if an owner is specified, assign rights
                if settings.MATERIALIZED_VIEWS_OWNER_TPL:
                    db_schema_name = MaterializedView.make_db_schema_name(site)

                    schema_owner = Template(
                        settings.MATERIALIZED_VIEWS_OWNER_TPL
                    ).substitute(
                        site_name=site.name,
                        site_slug=make_site_slug(site=site),
                    )

                    self.stdout.write(
                        f"  ++ Assigning permissions to '{schema_owner}' on schema '{db_schema_name}'"
                    )

                    self._assign_permissions_to_owner(
                        cursor,
                        db_schema_name,
                        schema_owner,
                    )

    def handle(self, *args, **options):
        for site in Site.objects.order_by("id"):
            self._create_views_for_site(site, **options)
