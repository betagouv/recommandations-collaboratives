from django.db import models

from recoco.apps.plugins.models import PluginModel


class Note(PluginModel):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title
