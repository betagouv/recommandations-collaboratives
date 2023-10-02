"""
app configuraiton to tasks

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-09-05 11:03:21 CEST
"""

from django.apps import AppConfig
from watson import search as watson


class TaskConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "urbanvitaliz.apps.tasks"

    def ready(self):
        from actstream import registry  # noqa

        registry.register(self.get_model("Task"))
        # registry.register(self.get_model("Document"))


# eof
