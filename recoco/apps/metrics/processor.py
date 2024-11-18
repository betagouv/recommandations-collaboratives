import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.backends.utils import CursorWrapper
from django.db.models import QuerySet

from .utils import metrics_db_schema_name


class MaterializedViewSpecError(Exception):
    pass


@dataclass
class MaterializedViewSqlQuery:
    sql: str
    params: tuple[Any] | None = None

    def __post_init__(self):
        self.sql = self.sql.replace("\n", "").strip()
        if self.sql.endswith(";"):
            self.sql = self.sql[:-1]


class MaterializedView:
    site: Site | None
    name: str
    cursor: CursorWrapper
    indexes: list[str]
    unique_indexes: list[str]

    def __init__(
        self,
        site: Site | None,
        name: str,
        indexes: list[str] = None,
        unique_indexes: list[str] = None,
        db_owner: str = None,
    ):
        self.site = site
        self.name = name
        self.cursor = None
        self.indexes = indexes or []
        self.unique_indexes = unique_indexes or []
        self.db_owner = db_owner

    @classmethod
    def from_spec(
        cls,
        spec: dict[str, Any],
        site: Site | None = None,
        check_sql_query: bool = True,
    ) -> "MaterializedView":
        try:
            materialized_view = MaterializedView(site, **spec)
        except TypeError as exc:
            raise MaterializedViewSpecError(
                f"Invalid materialized view specification '{spec}'"
            ) from exc

        if check_sql_query and materialized_view.get_sql_query() is None:
            raise MaterializedViewSpecError(
                f"SQL query for materialized view '{materialized_view.name}' is not found"
            )

        return materialized_view

    def __str__(self) -> str:
        name = self.name
        if self.site:
            name = f"{name} ({self.site.domain})"
        return name

    @property
    def db_view_name(self) -> str:
        return self.name

    @property
    def db_schema_name(self) -> str:
        return metrics_db_schema_name(site=self.site)

    @property
    def site_id(self) -> int | None:
        return self.site.id if self.site else None

    def set_cursor(self, cursor: CursorWrapper | None) -> None:
        self.cursor = cursor

    def get_django_sql_query(self) -> MaterializedViewSqlQuery | None:
        module_name = "{}.{}".format(
            str(
                Path(settings.METRICS_MATERIALIZED_VIEWS_SQL_DIR).relative_to(
                    settings.BASE_DIR.parent
                )
            ).replace("/", "."),
            self.name,
        )
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            return None

        queryset = module.get_queryset(site_id=self.site_id)

        if isinstance(queryset, QuerySet):
            sql, params = queryset.query.sql_with_params()
            return MaterializedViewSqlQuery(sql=sql, params=params)

    def get_raw_sql_query(self) -> MaterializedViewSqlQuery | None:
        sql_file = settings.METRICS_MATERIALIZED_VIEWS_SQL_DIR / f"{self.name}.sql"
        if not sql_file.exists():
            return None

        with open(sql_file, "r") as f:
            return MaterializedViewSqlQuery(sql=f.read(), params=(self.site_id,))

    def get_sql_query(self) -> MaterializedViewSqlQuery | None:
        return self.get_django_sql_query() or self.get_raw_sql_query()

    def create(self) -> None:
        sql_query = self.get_sql_query()
        if sql_query is None:
            return

        # Create the schema if it does not exist
        self.cursor.execute(sql=f"CREATE SCHEMA IF NOT EXISTS {self.db_schema_name};")

        # Create the materialized view
        self.cursor.execute(
            sql=f"CREATE MATERIALIZED VIEW IF NOT EXISTS {self.db_schema_name}.{self.db_view_name} AS ( {sql_query.sql} ) WITH NO DATA;",
            params=sql_query.params,
        )

        # Create indexes if any
        for index in self.indexes:
            self.cursor.execute(
                sql=f"CREATE INDEX IF NOT EXISTS {index} ON {self.db_schema_name}.{self.db_view_name} ({index});"
            )

        # Create unique indexes if any
        for index in self.unique_indexes:
            self.cursor.execute(
                sql=f"CREATE UNIQUE INDEX IF NOT EXISTS {index} ON {self.db_schema_name}.{self.db_view_name} ({index});"
            )

    def drop(self) -> None:
        self.cursor.execute(
            sql=f"DROP MATERIALIZED VIEW IF EXISTS {self.db_schema_name}.{self.db_view_name};"
        )

    def refresh(self) -> None:
        self.cursor.execute(
            sql=f"REFRESH MATERIALIZED VIEW {self.db_schema_name}.{self.db_view_name};"
        )
