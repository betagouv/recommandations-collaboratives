from django.apps import AppConfig
from watson import search as watson


class AddressbookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.addressbook"

    def _watson_registrations(self):
        from .adapters import ContactSearchAdapter, OrganizationSearchAdapter

        watson.register(self.get_model("Organization"), OrganizationSearchAdapter)
        watson.register(self.get_model("Contact"), ContactSearchAdapter)

    def _actstream_registrations(self):
        from actstream import registry

        registry.register(self.get_model("Organization"))

    def ready(self):
        from . import signals  # noqa: F401

        self._watson_registrations()
        self._actstream_registrations()
