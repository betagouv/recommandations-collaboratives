from django.apps import AppConfig
from watson import search as watson


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.home"

    def ready(self):
        import recoco.apps.home.signals  # noqa
        from actstream import registry
        from django.contrib.auth.models import User

        registry.register(User)
        watson.register(User)
