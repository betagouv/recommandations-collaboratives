import os
import random
import string
from io import StringIO

import pytest
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.db import connection

from .base import BaseClassTestMixin


class TestCommand(BaseClassTestMixin):
    @pytest.mark.django_db(transaction=True)
    def test_options_error(self):
        output = StringIO()
        call_command(
            "update_materialized_views",
            stdout=output,
            drop_only=True,
            refresh_only=True,
        )
        assert "You can't use both" in output.getvalue()

    @pytest.mark.django_db(transaction=True)
    def test_full_command(self, settings):
        random_prefix = "".join(
            random.choices(string.ascii_lowercase, k=10)  # noqa: S311
        )
        settings.METRICS_PREFIX = f"metrics_{random_prefix}"

        assert Site.objects.count() == 1

        call_command("update_materialized_views")

        with connection.cursor() as cursor:
            for schema_name in (
                f"metrics_{random_prefix}",
                f"metrics_{random_prefix}_example_com",
            ):
                cursor.execute(
                    f"SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'view_test_django_qs' AND schemaname = '{schema_name}';"
                )
                assert cursor.fetchone()[0] == 1
                cursor.execute(
                    f"SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'view_test_raw_sql' AND schemaname = '{schema_name}';"
                )
                assert cursor.fetchone()[0] == 1

            cursor.execute(
                f"SELECT COUNT(*) FROM pg_roles WHERE rolname='metrics_{random_prefix}_owner';"
            )
            assert cursor.fetchone()[0] == 0
            cursor.execute(
                f"SELECT COUNT(*) FROM pg_roles WHERE rolname='metrics_{random_prefix}_owner_example_com';"
            )
            assert cursor.fetchone()[0] == 0

    @pytest.mark.skipif(
        os.environ.get("SKIP_TEST_METRICS_CREATE_ROLES") == "true",
        reason="Skipping metrics tests that create roles",
    )
    @pytest.mark.django_db(transaction=True)
    def test_full_command_create_roles(self, settings):
        random_prefix = "".join(
            random.choices(string.ascii_lowercase, k=10)  # noqa: S311
        )
        settings.METRICS_PREFIX = f"metrics_{random_prefix}"

        call_command("update_materialized_views", create_roles=True)

        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM pg_roles WHERE rolname='metrics_{random_prefix}_owner';"
            )
            assert cursor.fetchone()[0] == 1
            cursor.execute(
                f"SELECT COUNT(*) FROM pg_roles WHERE rolname='metrics_{random_prefix}_owner_example_com';"
            )
            assert cursor.fetchone()[0] == 1
