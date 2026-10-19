from .utils import is_plugin_label


class TenantPluginRouter:
    """
    A router to control which models are migrated to which schema:
     - The "plugin_" apps go to their own plugin schema (see migrate_plugins)
     - Others to the public one
    """

    # Global flag to allow migration of extensions (plugin_*)
    is_plugin_operation = False

    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Identify if the app is an extension
        if is_plugin_label(app_label):
            # Do not fail by erroring, the main migrate would fail too early
            return self.is_plugin_operation or hints.get("is_plugin_operation", False)

        # Core apps go to the public schema only, never to plugin schemas
        return not self.is_plugin_operation
