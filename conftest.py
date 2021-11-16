"""
configuration for pytest

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-11-16 09:36:12 CET
"""

import pytest

from django.contrib.auth import models as auth


@pytest.fixture(autouse=True, scope="function")
def fix_groups_permissions(db):
    g = auth.Group.objects.get(name="switchtender")
    p = auth.Permission.objects.get(codename="can_administrate_project")
    g.permissions.add(p)


# eof
