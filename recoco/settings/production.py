# coding: utf-8

"""
Production settings for recoco-django
"""

from .common import *  # noqa

import os
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from recoco import __version__ as VERSION

DEBUG = False

# logging: send email and log to file 500 internal server errors

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "../errors.log",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": True,
        }
    },
}

# HTTPS and Security Settings
SECURE_HSTS_SECONDS = (
    31536000  # Future requests for the next year should use HTTPS only
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"

X_FRAME_OPTIONS = "DENY"

WAGTAILADMIN_BASE_URL = "recoconseil.fr"

# Sentry
if SENTRY_DSN := os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        environment="production" if not DEBUG else "dev",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        send_default_pii=True,
        release=f"recoco@{VERSION}",
    )

# eof
