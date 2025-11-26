# encoding: utf-8

"""
Forms for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-12-14 10:36:20 CEST
"""

from django import forms
from django.db.models import QuerySet
from markdownx.fields import MarkdownxFormField

from recoco.apps.addressbook.models import Contact

from . import models

##################################################
# Notes
##################################################


class NoteForm(forms.ModelForm):
    """Generic Note creation/edition"""

    class Meta:
        model = models.Note
        fields = ["content", "contact"]

    content = MarkdownxFormField()

    def set_contact_queryset(self, contact_queryset: QuerySet[Contact]):
        self.fields["contact"].queryset = contact_queryset


class StaffNoteForm(NoteForm):
    class Meta:
        model = models.Note
        fields = ["content", "contact"]


class PrivateNoteForm(forms.ModelForm):
    """Private Note creation"""

    class Meta:
        model = models.Note
        fields = ["content", "contact"]

    def set_contact_queryset(self, contact_queryset: QuerySet[Contact]):
        self.fields["contact"].queryset = contact_queryset


##################################################
# Project
##################################################
class ProjectForm(forms.ModelForm):
    """Form for updating the base information of a project"""

    postcode = forms.CharField(max_length=5, required=False, label="Code Postal")
    insee = forms.CharField(max_length=5, required=False, label="Commune")

    class Meta:
        model = models.Project
        fields = [
            "name",
            "postcode",
            "insee",
            "location",
            "description",
        ]

        labels = {
            "location": "Adresse",
            "description": "Contexte du dossier",
        }


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = ["the_file", "the_link", "description"]


class ProjectTagsForm(forms.ModelForm):
    """Form for tags creation/update"""

    class Meta:
        model = models.Project
        fields = ["tags"]
        help_texts = {
            "tags": 'Séparez vos tags par des virgules. Mettez les entre-guillemets quand c\'est une expression ou un mot composé. Par exemple : convention, "programme NAP", "plan d\'action"'
        }


class TopicForm(forms.Form):
    """Form for handling a topic"""

    name = forms.CharField(max_length=32, required=False, label="Thème")


class ProjectTopicsForm(forms.ModelForm):
    """Form for topics creation/update"""

    class Meta:
        model = models.Project
        fields = ["advisors_note"]


class ProjectModerationForm(forms.Form):
    """Form to add options to moderation"""

    join = forms.BooleanField(initial=False)


class ProjectActiveForm(forms.ModelForm):
    """Form to set/unset a project inactive"""

    class Meta:
        model = models.Project
        fields = ["inactive_reason"]


class ProjectLocationForm(forms.ModelForm):
    """Form for location update"""

    class Meta:
        model = models.Project
        fields = ["location_x", "location_y"]


# eof
