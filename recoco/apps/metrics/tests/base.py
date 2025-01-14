import pytest


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
