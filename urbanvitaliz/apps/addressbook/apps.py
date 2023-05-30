from django.apps import AppConfig
from watson import search as watson


class AddressbookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.addressbook"

    def ready(self):
        watson.register(
            self.get_model("Organization"),
            fields=("name", "departments__name", "departments__code"),
        )
