from django.apps import AppConfig


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.projects"

    def ready(self):
        import urbanvitaliz.apps.projects.signals  # noqa
        from actstream import registry  # noqa

        registry.register(self.get_model("Project"))
        registry.register(self.get_model("Task"))
        registry.register(self.get_model("Note"))
