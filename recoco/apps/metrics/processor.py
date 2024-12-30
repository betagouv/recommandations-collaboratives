import importlib
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import connection
from django.db.backends.utils import CursorWrapper
from django.db.models import QuerySet

from recoco.utils import make_site_slug


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


@dataclass
class MaterializedViewIndex:
    name: str
    columns: str
    unique: bool = False
    for_site: bool = True


class MaterializedView:
    name: str
    indexes: list[MaterializedViewIndex]
    cursor: CursorWrapper
    db_schema_name: str
    db_schema_owner: str

    def __init__(
        self,
        name: str,
        indexes: list[dict[str, Any]] = None,
    ):
        self.name = name
        self.indexes = [MaterializedViewIndex(**index) for index in indexes or []]
        self.cursor = None
        self.db_schema_name = settings.METRICS_PREFIX
        self.db_schema_owner = f"{settings.METRICS_PREFIX}_owner"

    @classmethod
    def from_spec(
        cls, spec: dict[str, Any], check_sql_query: bool = True
    ) -> "MaterializedView":
        try:
            materialized_view = MaterializedView(**spec)
        except TypeError as exc:
            raise MaterializedViewSpecError(
                f"Invalid materialized view specification '{spec}'"
            ) from exc

        if check_sql_query and materialized_view.get_sql_query() is None:
            raise MaterializedViewSpecError(
                f"SQL query for materialized view '{materialized_view.name}' is not found"
            )

        return materialized_view

    @property
    def db_view_name(self) -> str:
        return self.name

    @property
    def db_name(self) -> str:
        return connection.settings_dict["NAME"]

    def site_db_schema_name(self, site: Site) -> str:
        site_slug = make_site_slug(site=site)
        return f"{self.db_schema_name}_{site_slug}"

    def site_db_schema_owner(self, site: Site) -> str:
        site_slug = make_site_slug(site=site)

        if template := settings.METRICS_MATERIALIZED_VIEWS_OWNER_TPL:
            schema_owner = Template(template).substitute(site_slug=site_slug)
        else:
            schema_owner = f"{self.db_schema_owner}_{site_slug}"

        return (
            settings.METRICS_MATERIALIZED_VIEWS_OWNER_OVERRIDES.get(schema_owner, None)
            or schema_owner
        )

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

        queryset = module.get_queryset()

        if isinstance(queryset, QuerySet):
            sql, params = queryset.query.sql_with_params()
            return MaterializedViewSqlQuery(sql=sql, params=params)

    def get_raw_sql_query(self) -> MaterializedViewSqlQuery | None:
        sql_file = settings.METRICS_MATERIALIZED_VIEWS_SQL_DIR / f"{self.name}.sql"
        if not sql_file.exists():
            return None

        with open(sql_file, "r") as f:
            return MaterializedViewSqlQuery(sql=f.read())

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
            is_unique = "UNIQUE " if index.unique else ""
            self.cursor.execute(
                sql=f"CREATE {is_unique}INDEX IF NOT EXISTS {index.name} ON {self.db_schema_name}.{self.db_view_name} ({index.columns});"
            )

    def create_for_site(self, site: Site) -> None:
        site_db_schema_name = self.site_db_schema_name(site)

        # Create the site schema if it does not exist
        self.cursor.execute(sql=f"CREATE SCHEMA IF NOT EXISTS {site_db_schema_name};")

        # Create the site materialized view
        site_sql_query = f"SELECT * FROM {self.db_schema_name}.{self.db_view_name} WHERE site_domain = '{site.domain}'"
        self.cursor.execute(
            sql=f"CREATE MATERIALIZED VIEW IF NOT EXISTS {site_db_schema_name}.{self.db_view_name} AS ( {site_sql_query} ) WITH NO DATA;"
        )

        # Create indexes if any
        for index in self.indexes:
            if not index.for_site:
                continue
            is_unique = "UNIQUE " if index.unique else ""
            self.cursor.execute(
                sql=f"CREATE {is_unique}INDEX IF NOT EXISTS {index.name} ON {site_db_schema_name}.{self.db_view_name} ({index.columns});"
            )

    def drop(self) -> None:
        self.cursor.execute(
            sql=f"DROP MATERIALIZED VIEW IF EXISTS {self.db_schema_name}.{self.db_view_name};"
        )

    def drop_for_site(self, site: Site) -> None:
        self.cursor.execute(
            sql=f"DROP MATERIALIZED VIEW IF EXISTS {self.site_db_schema_name(site)}.{self.db_view_name};"
        )

    def refresh(self) -> None:
        self.cursor.execute(
            sql=f"REFRESH MATERIALIZED VIEW {self.db_schema_name}.{self.db_view_name};"
        )

    def refresh_for_site(self, site: Site) -> None:
        self.cursor.execute(
            sql=f"REFRESH MATERIALIZED VIEW {self.site_db_schema_name(site)}.{self.db_view_name};"
        )

    def assign_permissions(self) -> None:
        self._assign_permissions(
            schema_name=self.db_schema_name,
            schema_owner=self.db_schema_owner,
        )

    def assign_permissions_for_site(self, site: Site) -> None:
        self._assign_permissions(
            schema_name=self.site_db_schema_name(site),
            schema_owner=self.site_db_schema_owner(site),
        )

    def _assign_permissions(self, schema_name: str, schema_owner: str) -> None:
        self.cursor.execute(
            sql=f"GRANT CONNECT ON DATABASE {self.db_name} TO {schema_owner};"
        )
        self.cursor.execute(
            sql=f"GRANT USAGE ON SCHEMA {schema_name} TO {schema_owner};"
        )
        self.cursor.execute(
            sql=f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema_name} TO {schema_owner};"
        )
