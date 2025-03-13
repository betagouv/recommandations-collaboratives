from django.apps import AppConfig
from watson import search as watson

# from .search import ProjectSearchAdapter


class ProjectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.projects"

    def _watson_registrations(self):
        from .models import ProjectSearchAdapter

        watson.register(self.get_model("Project"), ProjectSearchAdapter)
        watson.register(self.get_model("Topic"), fields=("name",))

    def _actstream_registrations(self):
        from actstream import registry

        registry.register(self.get_model("Project"))
        registry.register(self.get_model("Note"))
        registry.register(self.get_model("Document"))
        registry.register(self.get_model("UserProjectStatus"))

    def ready(self):
        import recoco.apps.projects.signals  # noqa

        self._watson_registrations()
        self._actstream_registrations()
