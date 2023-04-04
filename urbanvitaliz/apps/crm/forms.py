from django import forms
from markdownx.fields import MarkdownxFormField

from . import models


class CRMSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Rechercher dans le CRM"}),
    )


class CRMNoteForm(forms.ModelForm):
    """Generic Note creation/edition"""

    class Meta:
        model = models.Note
        fields = ["kind", "title", "content", "tags", "sticky"]

    content = MarkdownxFormField()


class ProjectAnnotationForm(forms.Form):

    tag = forms.CharField(required=True)


# eof
