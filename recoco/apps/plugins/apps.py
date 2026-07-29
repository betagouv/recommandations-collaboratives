from django.apps import AppConfig


class PluginsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.plugins"

    def ready(self):
        from .manager import get_plugin_manager

        get_plugin_manager()
