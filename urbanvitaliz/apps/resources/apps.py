from django.apps import AppConfig
from watson import search as watson


class ResourcesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.resources"

    def ready(self):
        Resource = self.get_model("Resource")
        watson.register(
            Resource,
            fields=(
                "title",
                "subtitle",
                "summary",
                "content",
                "tags",
            ),
        )
