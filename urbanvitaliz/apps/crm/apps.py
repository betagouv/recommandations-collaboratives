from django.apps import AppConfig
from watson import search as watson


class CrmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.crm"

    def ready(self):
        from actstream import registry

        ProjectAnnotations = self.get_model("ProjectAnnotations")
        watson.register(
            ProjectAnnotations,
            fields=(
                "tags",
                "project__name",
            ),
        )

        Note = self.get_model("Note")
        watson.register(
            Note,
            fields=(
                "title",
                "tags",
            ),
        )
        registry.register(Note)
