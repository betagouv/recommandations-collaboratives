from unittest.mock import Mock, patch

import pluggy
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import Value
from django.test import RequestFactory
from django.urls import reverse
from model_bakery import baker
from psycopg.sql import SQL, Identifier

from recoco.apps.home.models import SiteConfiguration
from recoco.apps.projects.context_processors import unread_notifications_processor
from recoco.utils import login

from .hooks import CrmSpec, NotificationSpec, ProjectSpec
from .manager import get_site_plugin_manager
from .middlewares import TenantPluginSchemaMiddleware
from .routers import TenantPluginRouter

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


def make_plugin_manager(*named_plugins):
    """Build a real PluginManager pre-loaded with the given (name, instance) pairs."""
    pm = pluggy.PluginManager("recoco")
    pm.add_hookspecs(ProjectSpec)
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


@pytest.mark.django_db
class TestTenantPluginSchemaMiddleware:
    """Ensure the Middleware will extend the DB path based on schema_name presence"""

    def test_does_nothing_if_no_site_config(self, middleware, request_mock):
        if hasattr(request_mock, "site_config"):
            delattr(request_mock, "site_config")

        with patch("django.db.connection.cursor") as mock_cursor:
            middleware(request_mock)
            mock_cursor.assert_not_called()

    def test_does_nothing_if_no_schema_name(
        self, middleware, request_mock, current_site
    ):
        site_config = baker.make(SiteConfiguration, site=current_site, schema_name=None)
        request_mock.site_config = site_config

        with patch("django.db.connection.cursor") as mock_cursor:
            middleware(request_mock)
            mock_cursor.assert_not_called()

    def test_sets_search_path_if_schema_name_present(
        self, middleware, request_mock, current_site
    ):
        site_config = baker.make(
            SiteConfiguration, site=current_site, schema_name="tenant_lyon"
        )
        request_mock.site_config = site_config

        with patch("django.db.connection.cursor") as mock_cursor:
            # We need to mock the context manager __enter__ to get the actual cursor mock
            cursor_instance = mock_cursor.return_value.__enter__.return_value

            middleware(request_mock)

            cursor_instance.execute.assert_called_once_with(
                SQL("SET search_path TO {}, public").format(Identifier("tenant_lyon"))
            )


@pytest.mark.django_db
def test_create_tenant_schema_signal(current_site):
    with patch("django.db.connection.cursor") as mock_cursor:
        cursor_instance = mock_cursor.return_value.__enter__.return_value

        baker.make(SiteConfiguration, site=current_site, schema_name="test_schema")

        expected = SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
            Identifier("test_schema")
        )
        cursor_instance.execute.assert_called_with(expected)


@pytest.mark.django_db
def test_create_tenant_schema_signal_no_schema_name(current_site):
    with patch("django.db.connection.cursor") as mock_cursor:
        cursor_instance = mock_cursor.return_value.__enter__.return_value

        # Saving SiteConfiguration without schema_name should not trigger schema creation
        baker.make(SiteConfiguration, site=current_site, schema_name=None)

        # Ensure no call to execute contains "CREATE SCHEMA"
        for call in cursor_instance.execute.call_args_list:
            assert "CREATE SCHEMA" not in call[0][0]


# --- MANAGEMENT COMMAND--#
@pytest.mark.django_db
def test_migrate_tenant_command_logic(current_site):
    # SiteConfiguration must exist before calling the command.
    # Created outside the cursor mock so the post_save signal (CREATE SCHEMA)
    # does not pollute the cursor call assertions below.
    baker.make(SiteConfiguration, site=current_site, schema_name="tenant_lyon")

    with patch(
        "recoco.apps.plugins.management.commands.migrate_tenant.call_command"
    ) as mock_migrate:
        with patch(
            "recoco.apps.plugins.management.commands.migrate_tenant.connection"
        ) as mock_conn:
            cursor_instance = mock_conn.cursor.return_value.__enter__.return_value
            # Return a truthy row so the schema-existence SELECT passes.
            cursor_instance.fetchone.return_value = (1,)

            assert TenantPluginRouter.is_tenant_operation is False

            call_command("migrate_tenant", "--schema", "tenant_lyon", "my_app")

            # Check router flag is back to False after execution
            assert TenantPluginRouter.is_tenant_operation is False

            # migrate_tenant sets search_path in three steps:
            # 1. SET search_path TO tenant_lyon        (before ensure_schema)
            # 2. SET search_path TO tenant_lyon, public (after core-migration copy)
            # 3. SET search_path TO public             (finally)
            # Schema creation (CREATE SCHEMA) is handled by the post_save signal
            # on SiteConfiguration, not by this command.
            calls = [call[0][0] for call in cursor_instance.execute.call_args_list]
            assert (
                SQL("SET search_path TO {}").format(Identifier("tenant_lyon")) in calls
            )
            assert (
                SQL("SET search_path TO {}, public").format(Identifier("tenant_lyon"))
                in calls
            )
            assert "SET search_path TO public" in calls

            # Ghost entries for core migrations must be inserted so Django
            # skips them in the plan and doesn't re-execute them in the tenant.
            assert any("django_migrations" in repr(c) for c in calls)

            # Check migrate was called with the correct app
            mock_migrate.assert_called_with("migrate", "my_app", verbosity=1)


# ---------------------------------------------------------------------------
# CRM hook extension points
# ---------------------------------------------------------------------------

FAKE_PLUGIN_NAME = "fake_crm_plugin"


def make_crm_plugin_manager(plugin):
    """Build a plugin manager registered with CrmSpec and the given plugin."""
    pm = pluggy.PluginManager("recoco")
    pm.add_hookspecs(ProjectSpec)
    pm.add_hookspecs(CrmSpec)
    pm.register(plugin, name=FAKE_PLUGIN_NAME)
    return pm


class FakeCrmPlugin:
    """Minimal plugin that adds a sentinel annotation + field + column."""

    @pluggy.HookimplMarker("recoco")
    def crm_project_list_annotations(self, request):
        return {"plugin_sentinel": Value(42)}

    @pluggy.HookimplMarker("recoco")
    def crm_project_list_extra_serializer_fields(self, request):
        return ["plugin_sentinel"]

    @pluggy.HookimplMarker("recoco")
    def crm_project_list_columns(self, request):
        return {
            "header": "Sentinel",
            "cell_html": '<td x-text="project.plugin_sentinel"></td>',
            "col_class": "col--small",
        }


@pytest.fixture
def site_with_fake_plugin(current_site):
    return baker.make(
        SiteConfiguration,
        site=current_site,
        enabled_plugins=[FAKE_PLUGIN_NAME],
    )


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
        self, client, project, current_site
    ):
        baker.make(SiteConfiguration, site=current_site, enabled_plugins=[])

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
        self, request, client, current_site
    ):
        baker.make(SiteConfiguration, site=current_site, enabled_plugins=[])

        pm = make_crm_plugin_manager(FakeCrmPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            with login(client, groups=["example_com_staff"]):
                response = client.get(reverse("crm-project-list"))

        assert response.status_code == 200
        assert response.context["plugin_columns"] == []


# ---------------------------------------------------------------------------
# Notification hook extension point
# ---------------------------------------------------------------------------

FAKE_NOTIFICATION_PLUGIN_NAME = "fake_notification_plugin"
FAKE_NOTIFICATION_VERB = "plugin_fake:custom_verb"


class FakeNotificationPlugin:
    """Minimal plugin contributing an extra notification verb."""

    @pluggy.HookimplMarker("recoco")
    def notification_project_verbs(self):
        return [FAKE_NOTIFICATION_VERB]


def make_notification_plugin_manager(plugin):
    pm = pluggy.PluginManager("recoco")
    pm.add_hookspecs(NotificationSpec)
    pm.register(plugin, name=FAKE_NOTIFICATION_PLUGIN_NAME)
    return pm


@pytest.mark.django_db
class TestNotificationProjectVerbsHook:
    def test_verb_added_when_plugin_enabled(self, current_site):
        site_config = baker.make(
            SiteConfiguration,
            site=current_site,
            enabled_plugins=[FAKE_NOTIFICATION_PLUGIN_NAME],
        )
        user = baker.make(get_user_model())
        request = RequestFactory().get("/")
        request.user = user
        request.site_config = site_config

        pm = make_notification_plugin_manager(FakeNotificationPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            context = unread_notifications_processor(request)

        assert FAKE_NOTIFICATION_VERB in context["show_project_verb_list"]

    def test_verb_absent_when_plugin_disabled(self, current_site):
        site_config = baker.make(
            SiteConfiguration, site=current_site, enabled_plugins=[]
        )
        user = baker.make(get_user_model())
        request = RequestFactory().get("/")
        request.user = user
        request.site_config = site_config

        pm = make_notification_plugin_manager(FakeNotificationPlugin())

        with patch("recoco.apps.plugins.manager.get_plugin_manager", return_value=pm):
            context = unread_notifications_processor(request)

        assert FAKE_NOTIFICATION_VERB not in context["show_project_verb_list"]
