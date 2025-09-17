from django.apps import AppConfig


class ConversationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.conversations"

    def ready(self):
        import recoco.apps.conversations.signals  # noqa
