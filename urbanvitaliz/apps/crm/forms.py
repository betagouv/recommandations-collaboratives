from django import forms
from markdownx.fields import MarkdownxFormField

from . import models


class CRMSearchForm(forms.Form):
    query = forms.CharField(max_length=200, required=True)


class CRMNoteForm(forms.ModelForm):
    """Generic Note creation/edition"""

    class Meta:
        model = models.Note
        fields = ["title", "content"]

    content = MarkdownxFormField()
