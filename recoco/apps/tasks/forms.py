# encoding: utf-8

"""
Forms for tasks application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-12-14 10:36:20 CEST
"""

from django import forms
from django.contrib.sites.models import Site
from django.db.models import Q
from markdownx.fields import MarkdownxFormField

from recoco.apps.projects import models as projects_models
from recoco.apps.resources import models as resources_models
from recoco.utils import is_staff_for_site

from . import models

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

    def __init__(self, user, *args, **kwargs):
        super(PushTypeActionForm, self).__init__(*args, **kwargs)

        # Allow only projects on the current site with a usable status
        current_site = Site.objects.get_current()

        project_qs = projects_models.Project.objects.filter(
            sites=current_site,
        ).select_related("commune__department")

        if not is_staff_for_site(user, site=current_site):
            project_qs = project_qs.filter(switchtenders=user)

        project_qs = project_qs.exclude(
            Q(project_sites__status__in=["DRAFT", "REJECTED"]),
            ~Q(project_sites__site=current_site),
        ).distinct()

        self.fields["project"].queryset = project_qs

    PUSH_TYPES = (
        ("single", "single"),
        ("external_resource", "external_resource"),
        ("noresource", "noresource"),
    )

    push_type = forms.ChoiceField(choices=PUSH_TYPES)
    next = forms.CharField(required=False)
    project = forms.ModelChoiceField(
        queryset=projects_models.Project.objects.none(),
        empty_label="(Veuillez sélectionner un projet)",
        required=True,
    )


class CreateActionBaseForm(forms.ModelForm):
    """Base form for action creation"""

    topic_name = forms.CharField(required=False)


class CreateActionWithoutResourceForm(CreateActionBaseForm):
    """Create an action for a project, without attached resource"""

    class Meta:
        model = models.Task
        fields = ["intent", "content", "public"]


class CreateActionWithResourceForm(CreateActionBaseForm):
    resource = (
        forms.ModelChoiceField(
            queryset=resources_models.Resource.objects.exclude(
                status=resources_models.Resource.DRAFT
            ).with_ds_annotations()
        ),
    )

    def clean_resource(self):
        resource = self.cleaned_data["resource"]

        try:
            resource = (
                resources_models.Resource.on_site.exclude(
                    status=resources_models.Resource.DRAFT
                )
                .with_ds_annotations()
                .get(pk=resource.pk)
            )
        except resources_models.Resource.DoesNotExist:
            self.add_error(field="resource", error="Cette ressource n'existe pas")
            raise

        return resource

    class Meta:
        model = models.Task
        fields = ["intent", "content", "public", "resource"]


class CreateActionsFromResourcesForm(CreateActionBaseForm):
    resources = forms.ModelMultipleChoiceField(
        queryset=resources_models.Resource.objects.exclude(
            status=resources_models.Resource.DRAFT
        ).with_ds_annotations(),
        required=True,
    )

    def clean_resources(self):
        resources = self.cleaned_data["resources"]

        resources = (
            resources_models.Resource.on_site.exclude(
                status=resources_models.Resource.DRAFT
            )
            .with_ds_annotations()
            .filter(pk__in=[resource.pk for resource in resources.all()])
        )

        if resources.count() == 0:
            self.add_error("no_valid_resource", "Aucune ressource")
            raise ValueError("Aucune ressource")

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
    topic_name = forms.CharField(required=False)
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


# eof
