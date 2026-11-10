from django.apps import AppConfig
from django.db.backends.signals import connection_created


class PluginsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.plugins"

    def ready(self):
        from . import checks  # noqa: F401
        from .manager import get_plugin_manager
        from .utils import set_plugin_search_path_on_connection

        get_plugin_manager()
        connection_created.connect(
            set_plugin_search_path_on_connection, dispatch_uid="plugin_search_path"
        )
