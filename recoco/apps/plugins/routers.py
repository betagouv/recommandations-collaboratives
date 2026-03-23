class TenantPluginRouter:
    """
    A router to control which models are migrated to which schema:
     - The "plugin_" apps should go to tenant schema
     - Others to the public one
    """

    # Global flag to allow migration of extensions (plugin_*)
    is_tenant_operation = False

    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Identify if the app is an extension
        if app_label.startswith("plugin_"):
            # Do not fail by erroring, the main migrate would fail too early
            return self.is_tenant_operation or hints.get("is_tenant_operation", False)

        # Core apps always go to the default (public) schema
        return True
