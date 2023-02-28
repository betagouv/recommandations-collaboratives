# global personal configuration of pytest
import pytest

from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def setup_db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("update_permissions")


# eof
