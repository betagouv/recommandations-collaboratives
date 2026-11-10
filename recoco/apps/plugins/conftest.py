from io import StringIO

import pytest
from django.core.management import call_command
from model_bakery import baker

from recoco.apps.home.models import SiteConfiguration

from .resolvers import set_enabled_plugins
from .testing import PLUGIN


@pytest.fixture
def plugin_tables(db):
    call_command("migrate_plugins", PLUGIN, verbosity=0, stdout=StringIO())


@pytest.fixture
def enabled_plugins():
    """Enable plugins for the current thread, like the middleware does."""

    def enable(*plugins):
        set_enabled_plugins(list(plugins))

    yield enable
    set_enabled_plugins([])


@pytest.fixture
def site_with_enabled_plugins(current_site):
    """Factory: create a SiteConfiguration enabling the given plugin names."""

    def _make(names):
        return baker.make(
            SiteConfiguration, site=current_site, enabled_plugins=list(names)
        )

    return _make


@pytest.fixture
def site_without_plugins(current_site):
    return baker.make(SiteConfiguration, site=current_site, enabled_plugins=[])
