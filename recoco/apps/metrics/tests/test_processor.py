from io import StringIO
from unittest.mock import Mock, call

import pytest
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.db import connection
from django.db.backends.utils import CursorWrapper

from recoco.apps.metrics.processor import (
    MaterializedView,
    MaterializedViewSpecError,
)


class BaseClassTestMixin:
    @pytest.fixture(autouse=True)
    def _change_sql_dir(self, settings):
        settings.METRICS_MATERIALIZED_VIEWS_SQL_DIR = (
            settings.BASE_DIR / "apps/metrics/tests/sql_queries"
        )
        settings.METRICS_MATERIALIZED_VIEWS_SPEC = [
            {
                "name": "view_test_django_qs",
                "indexes": [
                    {
                        "name": "test_idx",
                        "columns": "id,site_domain",
                        "unique": True,
                        "for_site": False,
                    },
                    {
                        "name": "task_count_idx",
                        "columns": "task_count",
                        "unique": False,
                        "for_site": True,
                    },
                ],
            },
            {"name": "view_test_raw_sql"},
        ]


class TestMaterializedView(BaseClassTestMixin):
    @pytest.fixture(autouse=True)
    def stub_site(self):
        return Site(id=9, domain="example.com", name="site_name")

    def test_db_view_name(self):
        assert MaterializedView(name="view_test").db_view_name == "view_test"

    def test_db_schema_name(self):
        assert MaterializedView(name="view_test").db_schema_name == "metrics"

    def test_site_db_schema_name(self, stub_site):
        assert (
            MaterializedView(name="view_test").site_db_schema_name(site=stub_site)
            == "metrics_example_com"
        )

    def test_site_db_schema_owner(self, stub_site):
        assert (
            MaterializedView(name="view_test").site_db_schema_owner(site=stub_site)
            == "metrics_owner_example_com"
        )

    def test_from_spec_error(self, stub_site):
        with pytest.raises(MaterializedViewSpecError):
            MaterializedView.from_spec(
                spec={"name": "dummy_view_name"},
            )

    def test_create(self, settings):
        view = MaterializedView.from_spec(
            spec=settings.METRICS_MATERIALIZED_VIEWS_SPEC[0],
            check_sql_query=False,
        )
        mock_cursor = Mock(spec=CursorWrapper)
        view.set_cursor(mock_cursor)
        view.create()

        assert mock_cursor.execute.call_args_list == [
            call(sql="CREATE SCHEMA IF NOT EXISTS metrics;"),
            call(
                sql="CREATE MATERIALIZED VIEW IF NOT EXISTS metrics.view_test_django_qs AS"
                + ' ( SELECT "projects_project"."id", "django_site"."domain" AS "site_domain", COUNT("tasks_task"."id") AS "task_count" FROM "projects_project"'
                + ' LEFT OUTER JOIN "projects_projectsite" ON ("projects_project"."id" = "projects_projectsite"."project_id")'
                + ' LEFT OUTER JOIN "django_site" ON ("projects_projectsite"."site_id" = "django_site"."id")'
                + ' LEFT OUTER JOIN "tasks_task" ON ("projects_project"."id" = "tasks_task"."project_id")'
                + ' WHERE "projects_project"."deleted" IS NULL GROUP BY "projects_project"."id", 2 ) WITH NO DATA;',
                params=(),
            ),
            call(
                sql="CREATE UNIQUE INDEX IF NOT EXISTS test_idx ON metrics.view_test_django_qs (id,site_domain);"
            ),
            call(
                sql="CREATE INDEX IF NOT EXISTS task_count_idx ON metrics.view_test_django_qs (task_count);"
            ),
        ]

    def test_create_for_site(self, settings, stub_site):
        view = MaterializedView.from_spec(
            spec=settings.METRICS_MATERIALIZED_VIEWS_SPEC[0],
            check_sql_query=False,
        )
        mock_cursor = Mock(spec=CursorWrapper)
        view.set_cursor(mock_cursor)
        view.create_for_site(site=stub_site)

        assert mock_cursor.execute.call_args_list == [
            call(sql="CREATE SCHEMA IF NOT EXISTS metrics_example_com;"),
            call(
                sql="CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_example_com.view_test_django_qs"
                + " AS ( SELECT * FROM metrics.view_test_django_qs WHERE site_domain = 'example.com' ) WITH NO DATA;"
            ),
            call(
                sql="CREATE INDEX IF NOT EXISTS task_count_idx ON metrics_example_com.view_test_django_qs (task_count);"
            ),
        ]

    def test_refresh(self, settings):
        view = MaterializedView.from_spec(
            spec=settings.METRICS_MATERIALIZED_VIEWS_SPEC[0],
            check_sql_query=False,
        )
        mock_cursor = Mock(spec=CursorWrapper)
        view.set_cursor(mock_cursor)
        view.refresh()

        mock_cursor.execute.assert_called_once_with(
            sql="REFRESH MATERIALIZED VIEW metrics.view_test_django_qs;"
        )

    def test_refresh_for_site(self, settings, stub_site):
        view = MaterializedView.from_spec(
            spec=settings.METRICS_MATERIALIZED_VIEWS_SPEC[0],
            check_sql_query=False,
        )
        mock_cursor = Mock(spec=CursorWrapper)
        view.set_cursor(mock_cursor)
        view.refresh_for_site(site=stub_site)

        mock_cursor.execute.assert_called_once_with(
            sql="REFRESH MATERIALIZED VIEW metrics_example_com.view_test_django_qs;"
        )

    def test_drop(self, settings):
        view = MaterializedView.from_spec(
            spec=settings.METRICS_MATERIALIZED_VIEWS_SPEC[0],
            check_sql_query=False,
        )
        mock_cursor = Mock(spec=CursorWrapper)
        view.set_cursor(mock_cursor)
        view.drop()

        mock_cursor.execute.assert_called_once_with(
            sql="DROP MATERIALIZED VIEW IF EXISTS metrics.view_test_django_qs;"
        )

    def test_drop_for_site(self, settings, stub_site):
        view = MaterializedView.from_spec(
            spec=settings.METRICS_MATERIALIZED_VIEWS_SPEC[0],
            check_sql_query=False,
        )
        mock_cursor = Mock(spec=CursorWrapper)
        view.set_cursor(mock_cursor)
        view.drop_for_site(site=stub_site)

        mock_cursor.execute.assert_called_once_with(
            sql="DROP MATERIALIZED VIEW IF EXISTS metrics_example_com.view_test_django_qs;"
        )

    def test_assign_permissions(self, settings):
        view = MaterializedView.from_spec(
            spec=settings.METRICS_MATERIALIZED_VIEWS_SPEC[0],
            check_sql_query=False,
        )
        mock_cursor = Mock(spec=CursorWrapper)
        view.set_cursor(mock_cursor)
        view.assign_permissions()

        assert mock_cursor.execute.call_args_list == [
            call(sql=f"GRANT CONNECT ON DATABASE {view.db_name} TO metrics_owner;"),
            call(sql="GRANT USAGE ON SCHEMA metrics TO metrics_owner;"),
            call(sql="GRANT SELECT ON ALL TABLES IN SCHEMA metrics TO metrics_owner;"),
        ]

    def test_assign_permissions_for_site(self, settings, stub_site):
        view = MaterializedView.from_spec(
            spec=settings.METRICS_MATERIALIZED_VIEWS_SPEC[0],
            check_sql_query=False,
        )
        mock_cursor = Mock(spec=CursorWrapper)
        view.set_cursor(mock_cursor)
        view.assign_permissions_for_site(site=stub_site)

        assert mock_cursor.execute.call_args_list == [
            call(
                sql=f"GRANT CONNECT ON DATABASE {view.db_name} TO metrics_owner_example_com;"
            ),
            call(
                sql="GRANT USAGE ON SCHEMA metrics_example_com TO metrics_owner_example_com;"
            ),
            call(
                sql="GRANT SELECT ON ALL TABLES IN SCHEMA metrics_example_com TO metrics_owner_example_com;"
            ),
        ]


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
    def test_full_command(self):
        assert Site.objects.count() == 1

        call_command("update_materialized_views")

        with connection.cursor() as cursor:
            for schema_name in ("metrics", "metrics_example_com"):
                cursor.execute(
                    f"SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'view_test_django_qs' AND schemaname = '{schema_name}';"
                )
                assert cursor.fetchone()[0] == 1
                cursor.execute(
                    f"SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'view_test_raw_sql' AND schemaname = '{schema_name}';"
                )
                assert cursor.fetchone()[0] == 1
