from django.db import models

from recoco.apps.conversations.models import Node
from recoco.apps.plugins.models import PluginModel


class Note(PluginModel):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class NoteNode(Node):
    """A conversation node of a plugin, like plugins add to core messages."""

    note = models.ForeignKey(Note, on_delete=models.CASCADE)
