from django.apps import AppConfig
from watson import search as watson


class AddressbookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.addressbook"

    def ready(self):
        from actstream import registry

        Organization = self.get_model("Organization")
        watson.register(
            Organization,
            fields=("name", "departments__name", "departments__code"),
        )
        registry.register(Organization)
