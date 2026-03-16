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
            if not (
                self.is_tenant_operation or hints.get("is_tenant_operation", False)
            ):
                raise RuntimeError(
                    f"App '{app_label}' is a tenant plugin and cannot be migrated "
                    f"using the standard 'migrate' command. "
                    f"Use 'manage.py migrate_tenant --schema=<schema_name>' instead."
                )
            return True

        # Core apps always go to the default (public) schema
        return True
