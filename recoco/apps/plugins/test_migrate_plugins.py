from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from psycopg.sql import SQL, Identifier

from .management.commands.migrate_plugins import Command
from .routers import PluginRouter
from .utils import get_plugin_app_labels, get_plugin_search_path

PLUGIN = "plugin_testapp"


def migrate_plugins(*args):
    call_command("migrate_plugins", *args, verbosity=0, stdout=StringIO())


def table_exists(schema, table):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = %s AND table_name = %s",
            [schema, table],
        )
        return cursor.fetchone() is not None


def recorded_migrations(schema, app):
    with connection.cursor() as cursor:
        cursor.execute(
            SQL("SELECT name FROM {} WHERE app = %s").format(
                Identifier(schema, "django_migrations")
            ),
            [app],
        )
        return [row[0] for row in cursor.fetchall()]


def search_path():
    with connection.cursor() as cursor:
        cursor.execute("SHOW search_path")
        return cursor.fetchone()[0].replace(" ", "").split(",")


@pytest.mark.django_db
def test_migrate_plugins_creates_tables_in_plugin_schema():
    migrate_plugins(PLUGIN)

    assert table_exists(PLUGIN, "plugin_testapp_note")
    assert not table_exists("public", "plugin_testapp_note")


@pytest.mark.django_db
def test_migrate_plugins_records_migrations_in_plugin_schema():
    migrate_plugins(PLUGIN)

    assert table_exists(PLUGIN, "django_migrations")
    assert recorded_migrations(PLUGIN, PLUGIN) == ["0001_initial", "0002_notenode"]
    # Core migrations are copied over as ghost entries...
    assert "0001_initial" in recorded_migrations(PLUGIN, "sites")
    # ...but not the ones of other plugins
    with connection.cursor() as cursor:
        cursor.execute(
            SQL("SELECT DISTINCT app FROM {} WHERE app LIKE 'plugin%%'").format(
                Identifier(PLUGIN, "django_migrations")
            )
        )
        assert [row[0] for row in cursor.fetchall()] == [PLUGIN]


@pytest.mark.django_db
def test_migrate_plugins_is_safe_to_rerun():
    migrate_plugins(PLUGIN)
    migrate_plugins(PLUGIN)

    assert recorded_migrations(PLUGIN, PLUGIN) == ["0001_initial", "0002_notenode"]
    assert recorded_migrations(PLUGIN, "sites").count("0001_initial") == 1


@pytest.mark.django_db
def test_migrate_plugins_restores_router_flag_and_search_path():
    migrate_plugins(PLUGIN)

    assert PluginRouter.is_plugin_operation is False
    assert search_path() == get_plugin_search_path()


@pytest.mark.django_db
def test_migrate_plugins_rejects_non_plugin_app():
    with pytest.raises(CommandError):
        migrate_plugins("projects")


@pytest.mark.django_db
def test_migrate_plugins_without_label_migrates_every_installed_plugin():
    with patch.object(Command, "migrate_plugin") as migrate_plugin:
        migrate_plugins()

    migrated = [c.args[0] for c in migrate_plugin.call_args_list]
    assert PLUGIN in migrated
    assert migrated == get_plugin_app_labels()


def test_router_only_allows_plugin_migrations_during_plugin_operation():
    router = PluginRouter()

    assert router.allow_migrate("default", "projects") is True
    assert router.allow_migrate("default", PLUGIN) is False

    with patch.object(PluginRouter, "is_plugin_operation", True):
        assert router.allow_migrate("default", "projects") is False
        assert router.allow_migrate("default", PLUGIN) is True
