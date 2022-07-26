from django import forms
from markdownx.fields import MarkdownxFormField

from . import models


class CRMNoteForm(forms.ModelForm):
    """Generic Note creation/edition"""

    class Meta:
        model = models.Note
        fields = ["title", "content"]

    content = MarkdownxFormField()
