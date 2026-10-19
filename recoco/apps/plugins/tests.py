from unittest.mock import Mock, patch

import pluggy
import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import Value
from django.test import RequestFactory
from django.urls import reverse
from django.utils.safestring import mark_safe
from model_bakery import baker

from recoco.apps.home.models import SiteConfiguration
from recoco.apps.projects.context_processors import unread_notifications_processor
from recoco.utils import login

from .hooks import CrmSpec, NotificationSpec, ProjectSpec
from .manager import get_site_plugin_manager
from .middlewares import TenantPluginSchemaMiddleware
from .resolvers import get_enabled_plugins

# --- Fixtures & helpers for get_site_plugin_manager ---


@pytest.fixture
def get_response_mock():
    return Mock()


@pytest.fixture
def middleware(get_response_mock):
    return TenantPluginSchemaMiddleware(get_response=get_response_mock)


@pytest.fixture
def request_mock(enabled_plugins=None):
    return Mock()


hookimpl = pluggy.HookimplMarker("recoco")


class PluginA:
    @hookimpl
    def get_tab_views(self):
        return [{"name": "plugin_a"}]


class PluginB:
    @hookimpl
    def get_tab_views(self):
        return [{"name": "plugin_b"}]


def make_plugin_manager(*named_plugins, specs=(ProjectSpec,)):
    """Build a real PluginManager registered with the given hookspec namespaces
    and pre-loaded with the given (name, instance) pairs."""
    pm = pluggy.PluginManager("recoco")
    for spec in specs:
        pm.add_hookspecs(spec)
    for name, plugin in named_plugins:
        pm.register(plugin, name=name)
    return pm


def make_request(enabled_plugins):
    request = Mock()
    request.site_config.enabled_plugins = enabled_plugins
    return request


# --- Tests ---


class TestGetTenantHook:
    def test_returns_only_enabled_plugins(self):
        global_pm = make_plugin_manager(
            ("plugin_a", PluginA()), ("plugin_b", PluginB())
        )

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            request = make_request(["plugin_a"])
            scoped = get_site_plugin_manager(request)

        names = [name for name, _ in scoped.list_name_plugin()]
        assert "plugin_a" in names
        assert "plugin_b" not in names

    def test_returns_all_enabled_plugins(self):
        global_pm = make_plugin_manager(
            ("plugin_a", PluginA()), ("plugin_b", PluginB())
        )

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            request = make_request(["plugin_a", "plugin_b"])
            scoped = get_site_plugin_manager(request)

        names = [name for name, _ in scoped.list_name_plugin()]
        assert "plugin_a" in names
        assert "plugin_b" in names

    def test_returns_empty_manager_when_no_plugins_enabled(self):
        global_pm = make_plugin_manager(("plugin_a", PluginA()))

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            request = make_request([])
            scoped = get_site_plugin_manager(request)

        assert scoped.list_name_plugin() == []

    def test_ignores_unknown_plugin_names(self):
        global_pm = make_plugin_manager(("plugin_a", PluginA()))

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            request = make_request(["plugin_unknown"])
            scoped = get_site_plugin_manager(request)

        assert scoped.list_name_plugin() == []

    def test_hook_call_returns_results_from_enabled_plugins_only(self):
        global_pm = make_plugin_manager(
            ("plugin_a", PluginA()), ("plugin_b", PluginB())
        )

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            request = make_request(["plugin_a"])
            scoped = get_site_plugin_manager(request)

        results = [item for sublist in scoped.hook.get_tab_views() for item in sublist]
        assert {"name": "plugin_a"} in results
        assert {"name": "plugin_b"} not in results


@pytest.mark.django_db
class TestGetSitePluginManager:
    def test_returns_only_enabled_plugins(self, current_site):
        global_pm = make_plugin_manager(
            ("plugin_a", PluginA()), ("plugin_b", PluginB())
        )
        baker.make(SiteConfiguration, site=current_site, enabled_plugins=["plugin_a"])

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            scoped = get_site_plugin_manager(site=current_site)

        names = [name for name, _ in scoped.list_name_plugin()]
        assert "plugin_a" in names
        assert "plugin_b" not in names

    def test_returns_empty_manager_when_no_plugins_enabled(self, current_site):
        global_pm = make_plugin_manager(("plugin_a", PluginA()))
        baker.make(SiteConfiguration, site=current_site, enabled_plugins=[])

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            scoped = get_site_plugin_manager(site=current_site)

        assert scoped.list_name_plugin() == []

    def test_returns_empty_manager_when_no_site_configuration(self, current_site):
        global_pm = make_plugin_manager(("plugin_a", PluginA()))

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            scoped = get_site_plugin_manager(site=current_site)

        assert scoped.list_name_plugin() == []


def current_search_path():
    with connection.cursor() as cursor:
        cursor.execute("SHOW search_path")
        return cursor.fetchone()[0]


@pytest.mark.django_db
class TestTenantPluginSchemaMiddleware:
    """Ensure the Middleware enables the tenant's plugins for the request"""

    def capture_enabled_plugins(self, get_response_mock):
        seen = {}

        def get_response(request):
            seen["enabled_plugins"] = get_enabled_plugins()
            seen["search_path"] = current_search_path()

        get_response_mock.side_effect = get_response
        return seen

    def test_enables_no_plugin_if_no_site_config(
        self, middleware, get_response_mock, request_mock
    ):
        del request_mock.site_config
        seen = self.capture_enabled_plugins(get_response_mock)

        middleware(request_mock)

        assert seen["enabled_plugins"] == []

    def test_enables_site_plugins_during_request(
        self, middleware, get_response_mock, request_mock, current_site
    ):
        request_mock.site_config = baker.make(
            SiteConfiguration, site=current_site, enabled_plugins=["plugin_a"]
        )
        seen = self.capture_enabled_plugins(get_response_mock)

        middleware(request_mock)

        assert seen["enabled_plugins"] == ["plugin_a"]
        assert get_enabled_plugins() == []

    def test_does_not_touch_search_path(
        self, middleware, get_response_mock, request_mock, current_site
    ):
        request_mock.site_config = baker.make(
            SiteConfiguration,
            site=current_site,
            schema_name="tenant_lyon",
            enabled_plugins=["plugin_a"],
        )
        seen = self.capture_enabled_plugins(get_response_mock)
        before = current_search_path()

        middleware(request_mock)

        assert seen["search_path"] == before
        assert current_search_path() == before


# ---------------------------------------------------------------------------
# Shared helpers for hook extension point tests
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# CRM hook extension points
# ---------------------------------------------------------------------------

FAKE_PLUGIN_NAME = "fake_crm_plugin"


def make_crm_plugin_manager(plugin):
    """Build a plugin manager registered with CrmSpec and the given plugin."""
    return make_plugin_manager((FAKE_PLUGIN_NAME, plugin), specs=(ProjectSpec, CrmSpec))


class FakeCrmPlugin:
    """Minimal plugin that adds a sentinel annotation + field + column."""

    @hookimpl
    def crm_project_list_annotations(self, request):
        return {"plugin_sentinel": Value(42)}

    @hookimpl
    def crm_project_list_extra_serializer_fields(self, request):
        return ["plugin_sentinel"]

    @hookimpl
    def crm_project_list_columns(self, request):
        return {
            "header": "Sentinel",
            "cell_html": '<td x-text="project.plugin_sentinel"></td>',
            "col_class": "col--small",
        }


@pytest.fixture
def site_with_fake_plugin(site_with_enabled_plugins):
    return site_with_enabled_plugins([FAKE_PLUGIN_NAME])


@pytest.mark.django_db
class TestCrmProjectListAnnotationsHook:
    def test_annotation_is_applied_to_queryset(
        self, request, client, site_with_fake_plugin
    ):
        pm = make_crm_plugin_manager(FakeCrmPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            with login(client, groups=["example_com_staff"]):
                response = client.get(reverse("projects-list"))

        assert response.status_code == 200

    def test_extra_field_appears_in_rest_response(
        self, client, project, site_with_fake_plugin
    ):
        pm = make_crm_plugin_manager(FakeCrmPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            with login(client, groups=["example_com_staff"]):
                response = client.get(reverse("projects-list"))

        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) > 0
        assert "plugin_sentinel" in results[0]
        assert results[0]["plugin_sentinel"] == 42

    def test_extra_field_absent_when_plugin_disabled(
        self, client, project, site_without_plugins
    ):
        pm = make_crm_plugin_manager(FakeCrmPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            with login(client, groups=["example_com_staff"]):
                response = client.get(reverse("projects-list"))

        assert response.status_code == 200
        results = response.json()["results"]
        assert len(results) > 0
        assert "plugin_sentinel" not in results[0]


@pytest.mark.django_db
class TestCrmProjectListColumnsHook:
    def test_plugin_columns_in_view_context(
        self, request, client, site_with_fake_plugin
    ):
        pm = make_crm_plugin_manager(FakeCrmPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            with login(client, groups=["example_com_staff"]):
                response = client.get(reverse("crm-project-list"))

        assert response.status_code == 200
        columns = response.context["plugin_columns"]
        assert len(columns) == 1
        assert columns[0]["header"] == "Sentinel"

    def test_no_plugin_columns_when_plugin_disabled(
        self, request, client, site_without_plugins
    ):
        pm = make_crm_plugin_manager(FakeCrmPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            with login(client, groups=["example_com_staff"]):
                response = client.get(reverse("crm-project-list"))

        assert response.status_code == 200
        assert response.context["plugin_columns"] == []


# ---------------------------------------------------------------------------
# Project overview sidebar blocks hook extension point
# ---------------------------------------------------------------------------

FAKE_PROJECT_PLUGIN_NAME = "fake_project_plugin"


def make_project_plugin_manager(plugin):
    """Build a plugin manager registered with ProjectSpec and the given plugin."""
    return make_plugin_manager((FAKE_PROJECT_PLUGIN_NAME, plugin))


class FakeProjectOverviewPlugin:
    """Minimal plugin contributing a sidebar block to the project overview."""

    @hookimpl
    def project_overview_sidebar_blocks(self, project, request):
        return mark_safe("<div class='plugin-block-sentinel'>sentinel block</div>")


@pytest.fixture
def site_with_fake_project_plugin(site_with_enabled_plugins):
    return site_with_enabled_plugins([FAKE_PROJECT_PLUGIN_NAME])


@pytest.mark.django_db
class TestProjectOverviewSidebarBlocksHook:
    def test_block_rendered_in_sidebar(
        self, client, project, site_with_fake_project_plugin
    ):
        pm = make_project_plugin_manager(FakeProjectOverviewPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            with login(client, groups=["example_com_staff"]):
                response = client.get(
                    reverse("projects-project-detail-overview", args=[project.pk])
                )

        assert response.status_code == 200
        blocks = response.context["project_overview_sidebar_blocks"]
        assert len(blocks) == 1
        assert "plugin-block-sentinel" in blocks[0]
        assert b"<div class='plugin-block-sentinel'>" in response.content

    def test_no_block_when_plugin_disabled(self, client, project, site_without_plugins):
        pm = make_project_plugin_manager(FakeProjectOverviewPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            with login(client, groups=["example_com_staff"]):
                response = client.get(
                    reverse("projects-project-detail-overview", args=[project.pk])
                )

        assert response.status_code == 200
        assert response.context["project_overview_sidebar_blocks"] == []
        assert b"plugin-block-sentinel" not in response.content


# ---------------------------------------------------------------------------
# Notification hook extension point
# ---------------------------------------------------------------------------

FAKE_NOTIFICATION_PLUGIN_NAME = "fake_notification_plugin"
FAKE_NOTIFICATION_VERB = "plugin_fake:custom_verb"


class FakeNotificationPlugin:
    """Minimal plugin contributing an extra notification verb."""

    @hookimpl
    def notification_project_verbs(self):
        return [FAKE_NOTIFICATION_VERB]


def make_notification_plugin_manager(plugin):
    return make_plugin_manager(
        (FAKE_NOTIFICATION_PLUGIN_NAME, plugin), specs=(NotificationSpec,)
    )


@pytest.mark.django_db
class TestNotificationProjectVerbsHook:
    def test_verb_added_when_plugin_enabled(self, site_with_enabled_plugins):
        site_config = site_with_enabled_plugins([FAKE_NOTIFICATION_PLUGIN_NAME])
        user = baker.make(get_user_model())
        request = RequestFactory().get("/")
        request.user = user
        request.site_config = site_config

        pm = make_notification_plugin_manager(FakeNotificationPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            context = unread_notifications_processor(request)

        assert FAKE_NOTIFICATION_VERB in context["show_project_verb_list"]

    def test_verb_absent_when_plugin_disabled(self, site_without_plugins):
        user = baker.make(get_user_model())
        request = RequestFactory().get("/")
        request.user = user
        request.site_config = site_without_plugins

        pm = make_notification_plugin_manager(FakeNotificationPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            context = unread_notifications_processor(request)

        assert FAKE_NOTIFICATION_VERB not in context["show_project_verb_list"]
