from django.apps import AppConfig
from watson import search as watson


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.projects"

    def ready(self):
        import urbanvitaliz.apps.projects.signals  # noqa
        from actstream import registry  # noqa

        Project = self.get_model("Project")
        watson.register(
            Project,
            fields=(
                "name",
                "commune__name",
            ),
        )

        registry.register(Project)
        registry.register(self.get_model("Task"))
        registry.register(self.get_model("Note"))
        registry.register(self.get_model("Document"))
