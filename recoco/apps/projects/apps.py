from django.apps import AppConfig
from watson import search as watson

# from .search import ProjectSearchAdapter


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.projects"

    def ready(self):
        import recoco.apps.projects.signals  # noqa
        from actstream import registry  # noqa
        from .models import ProjectSearchAdapter

        Project = self.get_model("Project")
        watson.register(
            Project,
            ProjectSearchAdapter,
        )

        Topic = self.get_model("Topic")
        watson.register(
            Topic,
            fields=("name",),
        )

        registry.register(Project)
        registry.register(self.get_model("Note"))
        registry.register(self.get_model("Document"))
        registry.register(self.get_model("UserProjectStatus"))
