# coding: utf-8

"""
Production settings for urbanvitaliz-django
"""

from .common import *

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
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# eof
