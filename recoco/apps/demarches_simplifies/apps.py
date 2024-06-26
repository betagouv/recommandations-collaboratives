from django.apps import AppConfig


class DemarchesSimplifiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.demarches_simplifies"

    def ready(self):
        from . import signals  # noqa: F401
