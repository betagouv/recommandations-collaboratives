# encoding: utf-8

"""
Settings for frontend tests permissions

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2024-11-18 11:54:53 CEST
"""

import os

from .frontend_tests import *  # noqa: F403

DATABASES["default"]["NAME"] = os.getenv(  # noqa: F405
    "DJANGO_DB_TEST_NAME", "test_recoco"
)

# eof
