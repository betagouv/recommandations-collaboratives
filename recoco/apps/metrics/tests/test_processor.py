import pytest
from django.core.management import call_command
from unittest.mock import Mock, call
from django.db.backends.utils import CursorWrapper
from recoco.apps.metrics.processor import (
    MaterializedView,
    MaterializedViewSpecError,
)
from model_bakery import baker
from django.contrib.sites.models import Site
from recoco.apps.projects.models import Project
from django.db import connection


class TestMaterializedView:
    @pytest.fixture(autouse=True)
    def _change_sql_dir(self, settings):
        settings.MATERIALIZED_VIEWS_SQL_DIR = (
            settings.BASE_DIR / "apps/metrics/tests/sql_queries"
        )
        settings.MATERIALIZED_VIEWS_SPEC = [
            {"name": "view_test_django_qs"},
            {"name": "view_test_raw_sql"},
        ]

    def test_view_name(self, settings):
        assert (
            MaterializedView(site_id=9, name="view_test").db_view_name
            == "mv_9_view_test"
        )
        settings.MATERIALIZED_VIEWS_PREFIX = "prefix"
        assert (
            MaterializedView(site_id=9, name="view_test").db_view_name
            == "prefix_9_view_test"
        )

    def test_create_for_site(self):
        view = MaterializedView.create_for_site(
            site_id=9,
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

    def test_create_for_site_sql_query_error(self):
        with pytest.raises(MaterializedViewSpecError):
            MaterializedView.create_for_site(
                site_id=9,
                spec={"name": "dummy_view_name"},
            )
        MaterializedView.create_for_site(
            site_id=9,
            spec={"name": "view_test_django_qs"},
        )
        MaterializedView.create_for_site(
            site_id=9,
            spec={"name": "view_test_raw_sql"},
        )

    def test_drop(self):
        mock_cursor = Mock(spec=CursorWrapper)
        view = MaterializedView(site_id=9, name="view_test")
        view.set_cursor(mock_cursor)
        view.drop()
        mock_cursor.execute.assert_called_once_with(
            sql="DROP MATERIALIZED VIEW IF EXISTS mv_9_view_test;"
        )

    def test_refresh(self):
        mock_cursor = Mock(spec=CursorWrapper)
        view = MaterializedView(site_id=9, name="view_test")
        view.set_cursor(mock_cursor)
        view.refresh()
        mock_cursor.execute.assert_called_once_with(
            sql="REFRESH MATERIALIZED VIEW mv_9_view_test;"
        )

    def test_create_with_indexes(self):
        mock_cursor = Mock(spec=CursorWrapper)
        view = MaterializedView.create_for_site(
            site_id=9,
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
        assert len(calls) == 3
        assert calls[0] == call(
            sql='CREATE MATERIALIZED VIEW mv_9_view_test_simple AS ( select Count(*) from FROM "projects_project" ) WITH NO DATA;',
            params=(9,),
        )
        assert calls[1] == call(sql="CREATE INDEX ON mv_9_view_test_simple (idx);")
        assert calls[2] == call(
            sql="CREATE UNIQUE INDEX ON mv_9_view_test_simple (unique_idx);"
        )

    @pytest.mark.django_db(transaction=True)
    def test_command(self):
        assert Site.objects.count() == 1
        assert Site.objects.first().id == 1

        site = baker.make(Site)
        project = baker.make(Project)
        project.sites.add(site)

        call_command("update_materialized_views")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'mv_1_view_test_django_qs';"
            )
            assert cursor.fetchone()[0] == 1
            cursor.execute(
                "SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'mv_1_view_test_raw_sql';"
            )
            assert cursor.fetchone()[0] == 1

        call_command("update_materialized_views", "--drop-only")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'mv_1_view_test_django_qs';"
            )
            assert cursor.fetchone()[0] == 0
            cursor.execute(
                "SELECT COUNT(*) FROM pg_matviews WHERE matviewname = 'mv_1_view_test_raw_sql';"
            )
            assert cursor.fetchone()[0] == 0
