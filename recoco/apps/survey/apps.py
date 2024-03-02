from django.apps import AppConfig


class SurveyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.survey"

    def ready(self):
        import recoco.apps.survey.signals  # noqa
        from actstream import registry  # noqa

        registry.register(self.get_model("Survey"))
        registry.register(self.get_model("Session"))
