from django.apps import AppConfig


class SurveyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.survey"

    def ready(self):
        from actstream import registry

        registry.register(self.get_model("Survey"))
