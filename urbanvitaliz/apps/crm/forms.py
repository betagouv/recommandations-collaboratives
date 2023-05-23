from django import forms
from markdownx.fields import MarkdownxFormField

from urbanvitaliz.apps.home import models as home_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.addressbook import models as addressbook_models

from . import models


class CRMProfileForm(forms.ModelForm):
    """Update a user and her profile information"""

    first_name = forms.CharField(max_length=64, required=True)
    last_name = forms.CharField(max_length=64, required=True)

    class Meta:
        model = home_models.UserProfile
        fields = [
            "organization",
            "organization_position",
            "phone_no",
        ]


class CRMOrganizationForm(forms.ModelForm):
    """Update an organization"""

    class Meta:
        model = addressbook_models.Organization
        fields = ["name", "sites", "departments"]


class CRMAdvisorForm(forms.ModelForm):
    """Update an advisor profile department list"""

    class Meta:
        model = home_models.UserProfile
        fields = ["departments"]


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


class CRMProjectForm(forms.Form):
    """Update project properties"""

    notifications = forms.BooleanField(required=False)
    statistics = forms.BooleanField(required=False)


class ProjectAnnotationForm(forms.Form):
    tag = forms.CharField(required=True)


# eof
