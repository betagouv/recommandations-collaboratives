from django.apps import AppConfig


class DemarchesSimplifieesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.demarches_simplifiees"

    def ready(self):
        from . import signals  # noqa: F401
