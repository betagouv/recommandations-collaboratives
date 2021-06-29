# encoding: utf-8

"""
Utilities for urbanvitaliz project

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-06-29 09:16:14 CEST
"""

from contextlib import contextmanager

from django.core.exceptions import PermissionDenied

from django.contrib.auth import models as auth

from model_bakery.recipe import Recipe


########################################################################
# View helpers
########################################################################


def is_staff_or_403(user):
    """Raise a 403 error is user is not a staff member"""
    if not user or not user.is_staff:
        raise PermissionDenied("L'information demandée n'est pas disponible")


########################################################################
# Test helpers
########################################################################


@contextmanager
def login(client, is_staff=False):
    """Create a user and sign her into the application"""
    user = Recipe(auth.User, email="test@example.com", is_staff=is_staff).make()
    client.force_login(user)
    yield user


# eof
