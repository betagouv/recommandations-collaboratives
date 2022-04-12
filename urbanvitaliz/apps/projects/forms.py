# encoding: utf-8

"""
Forms for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-12-14 10:36:20 CEST
"""

from django import forms
from django.contrib.auth import models as auth_models
from markdownx.fields import MarkdownxFormField
from urbanvitaliz.apps.resources import models as resources_models

from . import models

##################################################
# Notes
##################################################


class NoteForm(forms.ModelForm):
    """Generic Note creation/edition"""

    class Meta:
        model = models.Note
        fields = ["content", "tags"]

    content = MarkdownxFormField()


class StaffNoteForm(NoteForm):
    class Meta:
        model = models.Note
        fields = ["content", "tags"]


class PrivateNoteForm(forms.ModelForm):
    """Private Note creation"""

    class Meta:
        model = models.Note
        fields = ["content"]


class PublicNoteForm(forms.ModelForm):
    """Public Note creation"""

    class Meta:
        model = models.Note
        fields = ["content"]


##################################################
# Tasks
##################################################


class TaskRecommendationForm(forms.ModelForm):
    """Form new task recommendation creation"""

    class Meta:
        model = models.TaskRecommendation
        fields = ["condition", "resource", "text", "departments"]


class TaskFollowupForm(forms.ModelForm):
    """Create a new followup for a task"""

    class Meta:
        model = models.TaskFollowup
        fields = ["comment"]


class UpdateTaskFollowupForm(forms.ModelForm):
    """Update a followup for a task"""

    class Meta:
        model = models.TaskFollowup
        fields = ["comment"]


class RsvpTaskFollowupForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, required=False)


class ResourceTaskForm(forms.ModelForm):
    """Create and task for push resource"""

    notify_email = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = models.Task
        fields = ["intent", "content", "contact", "notify_email"]


class PushTypeActionForm(forms.Form):
    """Determine which type of push it is"""

    PUSH_TYPES = (
        ("noresource", "noresource"),
        ("single", "single"),
        ("multiple", "multiple"),
    )

    push_type = forms.ChoiceField(choices=PUSH_TYPES)


class CreateActionWithoutResourceForm(forms.ModelForm):
    """Create an action for a project, without attached resource"""

    class Meta:
        model = models.Task
        fields = [
            "intent",
            "content",
            "public",
        ]


class CreateActionWithResourceForm(CreateActionWithoutResourceForm):
    resource = forms.ModelChoiceField(
        queryset=resources_models.Resource.objects.exclude(
            status=resources_models.Resource.DRAFT
        ),
        required=True,
    )

    class Meta:
        model = models.Task
        fields = ["intent", "content", "public", "resource"]


class CreateActionsFromResourcesForm(forms.ModelForm):
    resources = forms.ModelMultipleChoiceField(
        queryset=resources_models.Resource.objects.exclude(
            status=resources_models.Resource.DRAFT
        ),
        required=True,
    )

    class Meta:
        model = models.Task
        fields = ["resources", "public"]


class CreateTaskForm(forms.ModelForm):
    """Form new project task creation"""

    content = MarkdownxFormField(required=False)

    class Meta:
        model = models.Task
        fields = [
            "intent",
            "content",
            "public",
            "resource",
        ]


class UpdateTaskForm(forms.ModelForm):
    """Form for task update"""

    content = MarkdownxFormField(required=False)

    class Meta:
        model = models.Task
        fields = [
            "intent",
            "content",
            "resource",
            "public",
        ]


class RemindTaskForm(forms.Form):
    """Remind task after X days"""

    days = forms.IntegerField(min_value=0, required=False, initial=42)


##################################################
# Project
##################################################
class ProjectForm(forms.ModelForm):
    """Form for updating the base information of a project"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            st_group = auth_models.Group.objects.get(name="switchtender")
            self.fields["switchtenders"].queryset = (
                self.fields["switchtenders"]
                .queryset.filter(groups=st_group)
                .order_by("username")
            )
        except auth_models.Group.DoesNotExist:
            pass

    postcode = forms.CharField(max_length=5, required=False, label="Code Postal")
    publish_to_cartofriches = forms.BooleanField(
        label="Publication sur cartofriches", disabled=True, required=False
    )

    email = forms.CharField(label="Email principal", disabled=True, required=False)

    class Meta:
        model = models.Project
        fields = [
            "email",
            "first_name",
            "last_name",
            "org_name",
            "phone",
            "name",
            "postcode",
            "location",
            "description",
            "switchtenders",
            "publish_to_cartofriches",
            "muted",
        ]


class OnboardingForm(forms.ModelForm):
    """Form for onboarding a new local authority"""

    postcode = forms.CharField(max_length=5, required=False, label="Code Postal")

    class Meta:
        model = models.Project
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "org_name",
            "name",
            "location",
            "description",
            "impediments",
            "publish_to_cartofriches",
        ]


class SelectCommuneForm(forms.Form):
    def __init__(self, communes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commune"] = forms.ModelChoiceField(
            queryset=communes, widget=forms.RadioSelect, label="Votre commune :"
        )


# eof
