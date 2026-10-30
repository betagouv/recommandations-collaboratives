from io import StringIO

import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.management import call_command
from model_bakery import baker
from watson.models import SearchEntry

from recoco.apps.projects.models import Project

from .resolvers import set_enabled_plugins
from .search import tenant_search, tenant_search_models
from .testing.plugin_testapp.models import Note

PLUGIN = "plugin_testapp"


@pytest.fixture
def plugin_tables(db):
    call_command("migrate_plugins", PLUGIN, verbosity=0, stdout=StringIO())


@pytest.fixture
def enabled_plugins():
    def enable(*plugins):
        set_enabled_plugins(list(plugins))

    yield enable
    set_enabled_plugins([])


@pytest.fixture
def two_sites_notes(plugin_tables):
    site_a = Site.objects.get_current()
    site_b = baker.make(Site, domain="b.example.com")
    note_a = Note.objects.create(site=site_a, title="zeppelin from a")
    note_b = Note.objects.create(site=site_b, title="zeppelin from b")
    return site_a, site_b, note_a, note_b


def found_notes(results):
    return {entry.object for entry in results if isinstance(entry.object, Note)}


def test_search_returns_only_current_site_plugin_objects(
    two_sites_notes, enabled_plugins
):
    site_a, site_b, note_a, note_b = two_sites_notes
    enabled_plugins(PLUGIN)

    assert found_notes(tenant_search("zeppelin")) == {note_a}
    assert found_notes(tenant_search("zeppelin", models=(Note,))) == {note_a}

    with settings.SITE_ID.override(site_b.pk):
        assert found_notes(tenant_search("zeppelin")) == {note_b}


def test_search_skips_plugin_not_enabled_for_tenant(two_sites_notes, enabled_plugins):
    enabled_plugins()

    assert found_notes(tenant_search("zeppelin")) == set()
    # Not "every model", which is what watson does with an empty list
    assert list(tenant_search("zeppelin", models=(Note,))) == []


def test_search_scopes_plugin_querysets(two_sites_notes, enabled_plugins):
    site_a, site_b, note_a, note_b = two_sites_notes
    enabled_plugins(PLUGIN)

    results = tenant_search("zeppelin", models=(Note.objects.all(),))

    assert found_notes(results) == {note_a}


def test_search_models_leaves_core_models_alone(enabled_plugins):
    enabled_plugins()
    projects = Project.objects.filter(pk=1)

    assert tenant_search_models([Project, projects, Note]) == [Project, projects]


def test_buildwatson_indexes_each_site_object_separately(two_sites_notes):
    site_a, site_b, note_a, note_b = two_sites_notes
    SearchEntry.objects.all().delete()

    call_command("buildwatson", "plugin_testapp.Note", stdout=StringIO())

    indexed = SearchEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(Note)
    )
    assert sorted(indexed.values_list("title", flat=True)) == [
        "zeppelin from a",
        "zeppelin from b",
    ]
