from django.apps import AppConfig


class RemindersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.reminders"

    def ready(self):
        from actstream import registry

        registry.register(self.get_model("Reminder"))
