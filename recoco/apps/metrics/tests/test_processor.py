from unittest.mock import ANY, Mock, call

import pytest
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.db import connection
from django.db.backends.utils import CursorWrapper

from recoco.apps.metrics.processor import (
    MaterializedView,
    MaterializedViewSpecError,
)


class TestMaterializedView:
    @pytest.fixture(autouse=True)
    def _change_sql_dir(self, settings):
        settings.METRICS_MATERIALIZED_VIEWS_SQL_DIR = (
            settings.BASE_DIR / "apps/metrics/tests/sql_queries"
        )
        settings.METRICS_MATERIALIZED_VIEWS_SPEC = [
            {"name": "view_test_django_qs"},
            {"name": "view_test_raw_sql"},
        ]

    @pytest.fixture(autouse=True)
    def _disable_owner_settings(self, settings):
        """We disable that feature to prevent the test from required another role in
        the database"""
        settings.METRICS_MATERIALIZED_VIEWS_OWNER_TPL = None

    @pytest.fixture(autouse=True)
    def stub_site(self):
        return Site(id=9, domain="example.com", name="site_name")

    def test_db_view_name(self, settings, stub_site):
        assert (
            MaterializedView(site=stub_site, name="view_test").db_view_name
            == "view_test"
        )

    def test_db_schema_name(self, stub_site):
        assert (
            MaterializedView(site=stub_site, name="view_test").db_schema_name
            == "metrics_example_com"
        )

    def test_from_spec(self, stub_site):
        view = MaterializedView.from_spec(
            site=stub_site,
            spec={
                "name": "view_test",
                "indexes": ["index1", "index2"],
                "unique_indexes": ["unique_index1", "unique_index2"],
            },
            check_sql_query=False,
        )
        assert view.name == "view_test"
        assert view.indexes == ["index1", "index2"]
        assert view.unique_indexes == ["unique_index1", "unique_index2"]

    def test_from_spec_sql_query_error(self, stub_site):
        with pytest.raises(MaterializedViewSpecError):
            MaterializedView.from_spec(
                site=stub_site,
                spec={"name": "dummy_view_name"},
            )
        assert MaterializedView.from_spec(
            site=stub_site,
            spec={"name": "view_test_django_qs"},
        )
        assert MaterializedView.from_spec(
            site=stub_site,
            spec={"name": "view_test_raw_sql"},
        )

    def test_refresh(self, stub_site):
        mock_cursor = Mock(spec=CursorWrapper)
        view = MaterializedView(site=stub_site, name="view_test")
        view.set_cursor(mock_cursor)
        view.refresh()
        mock_cursor.execute.assert_called_once_with(
            sql="REFRESH MATERIALIZED VIEW metrics_example_com.view_test;"
        )

    def test_create_with_indexes(self, stub_site):
        mock_cursor = Mock(spec=CursorWrapper)
        view = MaterializedView.from_spec(
            site=stub_site,
            spec={
                "name": "view_test_simple",
                "indexes": ["idx"],
                "unique_indexes": ["unique_idx"],
            },
            check_sql_query=False,
        )
        view.set_cursor(mock_cursor)
        view.create()

        calls = mock_cursor.execute.call_args_list
        assert len(calls) == 4
        assert calls[0] == call(
            sql="CREATE SCHEMA IF NOT EXISTS metrics_example_com;",
        )
        assert calls[1] == call(
            sql='CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_example_com.view_test_simple AS ( select Count(*) from FROM "projects_project" ) WITH NO DATA;',
            params=(9,),
        )
        assert calls[2] == call(
            sql="CREATE INDEX IF NOT EXISTS idx ON metrics_example_com.view_test_simple (idx);"
        )
        assert calls[3] == call(
            sql="CREATE UNIQUE INDEX IF NOT EXISTS unique_idx ON metrics_example_com.view_test_simple (unique_idx);"
        )

    @pytest.mark.django_db(transaction=True)
    def test_assign_permissions_to_owner(self, mocker, settings):
        settings.METRICS_MATERIALIZED_VIEWS_OWNER_TPL = "metrics_owner_example_com"

        mocker.patch(
            "recoco.apps.metrics.management.commands.update_materialized_views.Command._check_user_exists_in_db",
            return_value=True,
        )

        mock = mocker.patch(
            "recoco.apps.metrics.management.commands.update_materialized_views.Command._assign_permissions_to_owner"
        )

        call_command("update_materialized_views")

        mock.assert_called_once_with(
            cursor=ANY,
            schema_name="metrics_example_com",
            schema_owner="metrics_owner_example_com",
        )

    @pytest.mark.django_db(transaction=True)
    def test_assign_permissions_to_owner_with_override(self, mocker, settings):
        owner_name = "my_overridden_user"
        settings.METRICS_MATERIALIZED_VIEWS_OWNER_TPL = "metrics_owner_example_com"
        settings.METRICS_MATERIALIZED_VIEWS_OWNER_OVERRIDES = {
            "example_com": owner_name
        }

        mocker.patch(
            "recoco.apps.metrics.management.commands.update_materialized_views.Command._check_user_exists_in_db",
            return_value=True,
        )
        mock = mocker.patch(
            "recoco.apps.metrics.management.commands.update_materialized_views.Command._assign_permissions_to_owner"
        )

        call_command("update_materialized_views")

        mock.assert_called_once_with(
            cursor=ANY,
            schema_name="metrics_example_com",
            schema_owner=owner_name,
        )

    @pytest.mark.django_db(transaction=True)
    def test_command(self):
        assert Site.objects.count() == 1

        call_command("update_materialized_views")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'view_test_django_qs' AND schemaname = 'metrics_example_com';"
            )
            assert cursor.fetchone()[0] == 1
            cursor.execute(
                "SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'view_test_raw_sql' AND schemaname = 'metrics_example_com';"
            )
            assert cursor.fetchone()[0] == 1
