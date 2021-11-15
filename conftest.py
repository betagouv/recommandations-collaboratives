import pytest

from django.contrib.auth import models as auth


@pytest.fixture(autouse=True, scope="function")
def fix_groups_permissions(db):
    g = auth.Group.objects.get(name="switchtender")
    p = auth.Permission.objects.get(codename="can_administrate_project")
    g.permissions.add(p)
