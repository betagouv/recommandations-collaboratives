from . import common
from .development import *  # noqa: F403

DS_AUTOLOAD_SCHEMA = False
CELERY_TASK_ALWAYS_EAGER = True

CONTENT_SECURITY_POLICY = common.CONTENT_SECURITY_POLICY

# Third-party plugins (enabled in a local development.py) have their own test
# suites, run with --ds=recoco.settings.development. Core tests only use the
# test plugin.
INSTALLED_APPS = tuple(  # noqa: F405
    app
    for app in INSTALLED_APPS  # noqa: F405
    if not app.startswith("plugin_")
) + ("recoco.apps.plugins.testing.plugin_testapp",)
