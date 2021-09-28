from django.apps import AppConfig


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.projects"

    def ready(self):
        from actstream import registry

        registry.register(self.get_model("Project"))
        registry.register(self.get_model("Task"))
