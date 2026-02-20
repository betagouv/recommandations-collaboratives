from django.apps import AppConfig
from watson import search as watson


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.home"

    def ready(self):
        import recoco.apps.home.signals  # noqa
        from actstream import registry
        from django.contrib.auth.models import User
        from recoco.apps.home.models import AdvisorAccessRequest

        registry.register(User)
        registry.register(AdvisorAccessRequest)
        watson.register(User)
