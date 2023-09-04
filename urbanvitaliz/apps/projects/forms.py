# encoding: utf-8

"""
Forms for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-12-14 10:36:20 CEST
"""


from django import forms
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
        fields = ["content"]

    content = MarkdownxFormField()


class StaffNoteForm(NoteForm):
    class Meta:
        model = models.Note
        fields = ["content"]


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
    next = forms.CharField(required=False)


class CreateActionWithoutResourceForm(forms.ModelForm):
    """Create an action for a project, without attached resource"""

    topic = forms.CharField(required=False)

    class Meta:
        model = models.Task
        fields = ["intent", "content", "public"]


class CreateActionWithResourceForm(CreateActionWithoutResourceForm):

    topic = forms.CharField(required=False)

    resource = (
        forms.ModelChoiceField(
            queryset=resources_models.Resource.objects.exclude(
                status=resources_models.Resource.DRAFT
            )
        ),
    )

    def clean_resource(self):
        resource = self.cleaned_data["resource"]

        try:
            resource = resources_models.Resource.on_site.exclude(
                status=resources_models.Resource.DRAFT
            ).get(pk=resource.pk)
        except resources_models.Resource.DoesNotExist:
            self.add_error("resource_unknown", "Cette ressource n'existe pas")
            raise None

        return resource

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

    def clean_resources(self):
        resources = self.cleaned_data["resources"]

        resources = resources_models.Resource.on_site.exclude(
            status=resources_models.Resource.DRAFT
        ).filter(pk__in=[resource.pk for resource in resources.all()])

        if resources.count() == 0:
            self.add_error("no_valid_resource", "Aucune ressource")
            raise None

        return resources

    class Meta:
        model = models.Task
        fields = ["resources", "public"]


class CreateTaskForm(forms.ModelForm):
    """Form new project task creation"""
    # TODO seems to not be used any more

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
    topic = forms.CharField(required=False)
    next = forms.CharField(required=False)

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

    postcode = forms.CharField(max_length=5, required=False, label="Code Postal")
    insee = forms.CharField(max_length=5, required=False, label="Code Insee")

    class Meta:
        model = models.Project
        fields = [
            "name",
            "postcode",
            "insee",
            "location",
            "description",
        ]


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = ["the_file", "the_link", "description"]


class ProjectTagsForm(forms.ModelForm):
    """Form for tags creation/update"""

    class Meta:
        model = models.Project
        fields = ["tags"]


class ProjectTopicsForm(forms.ModelForm):
    """Form for topics creation/update"""

    class Meta:
        model = models.Project
        fields = ["advisors_note"]


# eof
