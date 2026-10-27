from io import StringIO

import pytest
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.db import connection, connections

from .testing.plugin_testapp.models import Note
from .utils import get_plugin_app_labels, get_plugin_search_path

PLUGIN = "plugin_testapp"


def show_search_path(conn):
    with conn.cursor() as cursor:
        cursor.execute("SHOW search_path")
        return cursor.fetchone()[0].replace(" ", "").split(",")


def test_plugin_search_path_starts_with_public():
    assert get_plugin_search_path() == ["public", *get_plugin_app_labels()]
    assert PLUGIN in get_plugin_search_path()


@pytest.mark.django_db
def test_new_connection_gets_plugin_search_path():
    new_connection = connections.create_connection("default")
    try:
        assert show_search_path(new_connection) == get_plugin_search_path()
    finally:
        new_connection.close()


@pytest.mark.django_db
def test_plugin_models_resolve_without_schema_switch():
    call_command("migrate_plugins", PLUGIN, verbosity=0, stdout=StringIO())

    site = Site.objects.get_current()
    note = Note.objects.create(site=site, title="hello")

    assert show_search_path(connection) == get_plugin_search_path()
    assert Note.objects.get(pk=note.pk).title == "hello"
    assert list(Note.on_site.values_list("title", flat=True)) == ["hello"]
