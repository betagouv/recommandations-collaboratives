# encoding: utf-8

"""
Settings for frontend tests

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2024-11-18 11:54:53 CEST
"""

import os

from dotenv import load_dotenv

from .common import *

load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DJANGO_DEBUG = True

ALLOWED_HOSTS = ["localhost", "example.localhost"]

INSTALLED_APPS += (
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_extensions",
)

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# LOCAL DOCKER DATABASE
# DATABASES = {
#      'default': {
#          'ENGINE': 'django.db.backends.postgresql',
#          'NAME': os.environ.get('POSTGRES_NAME'),
#          'USER': os.environ.get('POSTGRES_USER'),
#          'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
#          'HOST': 'db',
#          'PORT': 5432,
#      }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME"),
        "USER": os.getenv("DJANGO_DB_USER"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD"),
        "HOST": os.getenv("DJANGO_DB_HOST"),
        "PORT": os.getenv("DJANGO_DB_PORT"),
        "TEST": {"NAME": os.getenv("DJANGO_DB_TEST_NAME")},
    }
}


# EMAIL
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SECRET_KEY = os.getenv("SECRET_KEY", "secret")

BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
BREVO_FORCE_DEBUG = True

# Recaptcha
RECAPTCHA_REQUIRED_SCORE = 0

# Vite
DJANGO_VITE_ASSETS_PATH = BASE_DIR / "frontend" / "dist"
DJANGO_VITE = {
    "default": {
        "dev_mode": False,
        "dev_server_port": 3001,
        "manifest_path": DJANGO_VITE_ASSETS_PATH / "manifest.json",
    }
}

MULTISITE_REPO_DIR = BASE_DIR / ".." / "multisites"
TEMPLATES[0]["DIRS"] += [MULTISITE_REPO_DIR / "templates"]
STATICFILES_DIRS += [MULTISITE_REPO_DIR / "static"]
STATICFILES_DIRS += [BASE_DIR / "static"]
STATICFILES_DIRS += [DJANGO_VITE_ASSETS_PATH]


# Uncomment Gdal and Geos libraries paths on MacOS
GDAL_LIBRARY_PATH = os.getenv("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = os.getenv("GEOS_LIBRARY_PATH")

SILENCED_SYSTEM_CHECKS += ["captcha.recaptcha_test_key_error"]

# Celery
CELERY_TASK_ALWAYS_EAGER = True

# Démarches simplifiées
DS_AUTOLOAD_SCHEMA = False
DS_AUTOCREATE_FOLDER = False

# eof
