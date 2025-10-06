from django.apps import AppConfig


class ConversationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.conversations"

    def _actstream_registrations(self):
        from actstream import registry

        registry.register(self.get_model("Message"))

    def ready(self):
        import recoco.apps.conversations.signals  # noqa

        self._actstream_registrations()
