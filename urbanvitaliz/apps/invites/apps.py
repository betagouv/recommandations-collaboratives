from django.apps import AppConfig


class InvitesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.invites"

    def ready(self):
        from actstream import registry  # noqa

        registry.register(self.get_model("Invite"))
