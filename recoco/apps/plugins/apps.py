from django.apps import AppConfig

from .manager import get_plugin_manager


class PluginsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.plugins"

    def ready(self):
        get_plugin_manager()
