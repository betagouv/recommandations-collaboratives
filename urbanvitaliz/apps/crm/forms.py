from django import forms
from markdownx.fields import MarkdownxFormField

from urbanvitaliz.apps.home import models as home_models
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
        fields = ["name", "departments"]


class CRMOrganizationMergeForm(forms.Form):
    """Merge multiple organizations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["org_ids"].choices = [
            (t.id, t.name) for t in addressbook_models.Organization.objects.all()
        ]

    name = forms.CharField(max_length=200, required=True)
    org_ids = forms.MultipleChoiceField()


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
