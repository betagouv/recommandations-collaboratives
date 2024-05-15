import pytest
from django.core.management import call_command
from django.db import connection
from django.contrib.sites.models import Site


@pytest.mark.django_db(transaction=True)
def test_rebuild_views():
    assert Site.objects.count() == 1

    call_command("update_materialized_views")

    for view_name in ("mv_switchtenders_conn_per_day",):
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM pg_matviews WHERE matviewname = '{view_name}' AND schemaname = 'metrics_example_com';"
            )
            assert cursor.fetchone()[0] == 1
            cursor.execute(
                f"SELECT COUNT(*) FROM pg_matviews WHERE matviewname = '{view_name}' AND schemaname = 'metrics_example_com';"
            )
            assert cursor.fetchone()[0] == 1

    call_command("update_materialized_views", "--drop-only")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM pg_matviews WHERE schemaname = 'metrics_example_com';"
        )
        assert cursor.fetchone()[0] == 0
