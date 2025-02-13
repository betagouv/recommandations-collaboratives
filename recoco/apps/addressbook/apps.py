from django.apps import AppConfig
from watson import search as watson


class AddressbookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.addressbook"

    def ready(self):
        from actstream import registry

        Organization = self.get_model("Organization")
        watson.register(
            Organization,
            fields=("name", "departments__name", "departments__code"),
        )

        Contact = self.get_model("Contact")
        watson.register(
            Contact,
            fields=(
                "last_name",
                "first_name",
                "email",
                "division",
                "organization__name",
                "organization__group__name",
                "organization__departments__name",
                "organization__departments__code",
                "organization__departments__region__name",
                "organization__departments__region__code",
            ),
        )

        registry.register(Organization)
