from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from recoco.apps.metrics.processor import (
    MaterializedView,
    MaterializedViewSpecError,
)


class Command(BaseCommand):
    help = "Update materialized view used for metrics"

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

    def handle(self, *args, **options):
        for site in Site.objects.order_by("id"):
            self._create_views_for_site(site, **options)
