from unittest.mock import Mock, patch

import pluggy
import pytest
from django.core.management import call_command
from model_bakery import baker

from recoco.apps.home.models import SiteConfiguration

from .hooks import ProjectSpec
from .manager import get_tenant_hook
from .middlewares import TenantPluginSchemaMiddleware
from .routers import TenantPluginRouter

# --- Fixtures & helpers for get_tenant_hook ---


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
            scoped = get_tenant_hook(request)

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
            scoped = get_tenant_hook(request)

        names = [name for name, _ in scoped.list_name_plugin()]
        assert "plugin_a" in names
        assert "plugin_b" in names

    def test_returns_empty_manager_when_no_plugins_enabled(self):
        global_pm = make_plugin_manager(("plugin_a", PluginA()))

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            request = make_request([])
            scoped = get_tenant_hook(request)

        assert scoped.list_name_plugin() == []

    def test_ignores_unknown_plugin_names(self):
        global_pm = make_plugin_manager(("plugin_a", PluginA()))

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            request = make_request(["plugin_unknown"])
            scoped = get_tenant_hook(request)

        assert scoped.list_name_plugin() == []

    def test_hook_call_returns_results_from_enabled_plugins_only(self):
        global_pm = make_plugin_manager(
            ("plugin_a", PluginA()), ("plugin_b", PluginB())
        )

        with patch(
            "recoco.apps.plugins.manager.get_plugin_manager", return_value=global_pm
        ):
            request = make_request(["plugin_a"])
            scoped = get_tenant_hook(request)

        results = [item for sublist in scoped.hook.get_tab_views() for item in sublist]
        assert {"name": "plugin_a"} in results
        assert {"name": "plugin_b"} not in results


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
                "SET search_path TO tenant_lyon, public"
            )


@pytest.mark.django_db
def test_create_tenant_schema_signal(current_site):
    with patch("django.db.connection.cursor") as mock_cursor:
        cursor_instance = mock_cursor.return_value.__enter__.return_value

        # Saving SiteConfiguration with schema_name should trigger the signal
        baker.make(SiteConfiguration, site=current_site, schema_name="test_schema")

        cursor_instance.execute.assert_called_with(
            "CREATE SCHEMA IF NOT EXISTS test_schema"
        )


@pytest.mark.django_db
def test_create_tenant_schema_signal_no_schema_name(current_site):
    with patch("django.db.connection.cursor") as mock_cursor:
        cursor_instance = mock_cursor.return_value.__enter__.return_value

        # Saving SiteConfiguration without schema_name should not trigger schema craetion
        baker.make(SiteConfiguration, site=current_site, schema_name=None)

        # Ensure no call to execute contains "CREATE SCHEMA"
        for call in cursor_instance.execute.call_args_list:
            assert "CREATE SCHEMA" not in call[0][0]


# --- MANAGEMENT COMMAND--#
@pytest.mark.django_db
def test_migrate_tenant_command_logic():
    # We mock migrate call_command and connection.cursor
    with patch(
        "recoco.apps.plugins.management.commands.migrate_tenant.call_command"
    ) as mock_migrate:
        with patch("django.db.connection.cursor") as mock_cursor:
            cursor_instance = mock_cursor.return_value.__enter__.return_value

            assert TenantPluginRouter.is_tenant_operation is False

            call_command("migrate_tenant", "--schema", "tenant_lyon", "my_app")

            # Check router was enabled during execution (we check it's back to False)
            assert TenantPluginRouter.is_tenant_operation is False

            # Check search_path was set
            # The order of calls should be:
            # 1- CREATE SCHEMA
            # 2- SET search_path TO tenant_lyon, public
            #  (migration)
            # 3- SET search_path TO public

            calls = [call[0][0] for call in cursor_instance.execute.call_args_list]
            assert "CREATE SCHEMA IF NOT EXISTS tenant_lyon" in calls
            assert "SET search_path TO tenant_lyon, public" in calls
            assert "SET search_path TO public" in calls

            # Check migrate was called with correct app
            mock_migrate.assert_called_with("migrate", "my_app", verbosity=1)
