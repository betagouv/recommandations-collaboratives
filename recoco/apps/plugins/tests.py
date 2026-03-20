from unittest.mock import Mock, patch

import pytest
from django.core.management import call_command
from model_bakery import baker

from recoco.apps.home.models import SiteConfiguration

from .middlewares import TenantPluginSchemaMiddleware
from .routers import TenantPluginRouter


@pytest.fixture
def get_response_mock():
    return Mock()


@pytest.fixture
def middleware(get_response_mock):
    return TenantPluginSchemaMiddleware(get_response=get_response_mock)


@pytest.fixture
def request_mock():
    return Mock()


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
