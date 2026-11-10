from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection, connections
from psycopg.sql import SQL, Identifier

from .management.commands.migrate_plugins import Command
from .routers import PluginRouter
from .testing import PLUGIN, current_search_path
from .utils import get_plugin_app_labels, get_plugin_search_path


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


def recorded_migrations(schema):
    with connection.cursor() as cursor:
        cursor.execute(
            SQL("SELECT app, name FROM {}").format(
                Identifier(schema, "django_migrations")
            )
        )
        return cursor.fetchall()


@pytest.mark.django_db
def test_migrate_plugins_creates_tables_in_plugin_schema():
    migrate_plugins(PLUGIN)

    assert table_exists(PLUGIN, "plugin_testapp_note")
    assert not table_exists("public", "plugin_testapp_note")


@pytest.mark.django_db
def test_migrate_plugins_records_migrations_once_in_plugin_schema():
    migrate_plugins(PLUGIN)
    migrate_plugins(PLUGIN)

    recorded = recorded_migrations(PLUGIN)
    assert [name for app, name in recorded if app == PLUGIN] == [
        "0001_initial",
        "0002_notenode",
    ]
    # Core migrations are copied over as ghost entries, but not the ones of
    # other plugins
    assert recorded.count(("sites", "0001_initial")) == 1
    assert {app for app, _ in recorded if app.startswith("plugin")} == {PLUGIN}


@pytest.mark.django_db
def test_migrate_plugins_restores_router_flag_and_search_path():
    migrate_plugins(PLUGIN)

    assert PluginRouter.is_plugin_operation is False
    assert current_search_path() == get_plugin_search_path()


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


@pytest.mark.django_db
def test_new_connection_gets_plugin_search_path():
    new_connection = connections.create_connection("default")
    try:
        assert current_search_path(new_connection) == get_plugin_search_path()
    finally:
        new_connection.close()
