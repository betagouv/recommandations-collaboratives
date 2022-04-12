from django.apps import AppConfig


class SurveyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.survey"

    def ready(self):
        import urbanvitaliz.apps.survey.signals  # noqa
        from actstream import registry  # noqa

        registry.register(self.get_model("Survey"))
        registry.register(self.get_model("Session"))
