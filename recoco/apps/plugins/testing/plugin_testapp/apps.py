from django.apps import AppConfig


class PluginTestappConfig(AppConfig):
    """A minimal plugin app, installed in test settings only."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.plugins.testing.plugin_testapp"
    label = "plugin_testapp"

    def ready(self):
        from actstream import registry
        from watson import search as watson

        registry.register(self.get_model("Note"))
        watson.register(self.get_model("Note"), fields=("title",))
