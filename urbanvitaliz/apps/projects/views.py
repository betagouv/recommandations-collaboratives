# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django.contrib.auth.decorators import login_required

from django import forms

from django.urls import reverse

from django.contrib import messages
from django.contrib.syndication.views import Feed

from django.utils import timezone

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from markdownx.fields import MarkdownxFormField

from urbanvitaliz.utils import is_staff_or_403
from urbanvitaliz.utils import send_email

from urbanvitaliz.apps.resources import models as resources
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.addressbook import models as addressbook_models

from . import models


########################################################################
# On boarding
########################################################################


def onboarding(request):
    """Return the onboarding page"""
    if request.method == "POST":
        form = OnboardingForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            postcode = form.cleaned_data.get("postcode")
            project.commune = geomatics.Commune.get_by_postal_code(postcode)
            project.save()
            models.Note(
                project=project, content=f"# Demande initiale\n\n{project.impediments}"
            ).save()
            return render(request, "projects/thanks.html", locals())
    else:
        form = OnboardingForm()
    return render(request, "projects/onboarding.html", locals())


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
        ]


########################################################################
# Local authorities
########################################################################


@login_required
def local_authority(request):
    """Return the projects followup for logged in local authority"""
    projects = models.Project.fetch(email=request.user.email)
    # store my projects in the session
    request.session["projects"] = list(
        {
            "name": p.name,
            "id": p.id,
            "location": p.location,
            "actions_open": p.tasks.open().count(),
        }
        for p in projects
    )
    return render(request, "projects/local_authority.html", locals())


########################################################################
# Switchtender
########################################################################


@login_required
def project_list(request):
    """Return the projects for the switchtender"""
    is_staff_or_403(request.user)
    projects = models.Project.fetch().order_by("-created_on")
    return render(request, "projects/project/list.html", locals())


@login_required
def project_detail(request, project_id=None):
    """Return the details of given project for switchtender"""
    project = get_object_or_404(models.Project, pk=project_id)
    # if user is not the owner then check for admin rights
    if project.email != request.user.email:
        is_staff_or_403(request.user)
    return render(request, "projects/project/detail.html", locals())


@login_required
def project_update(request, project_id=None):
    """Update the base information of a project"""
    is_staff_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_on = timezone.now()
            instance.save()
            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/project/update.html", locals())


@login_required
def project_accept(request, project_id=None):
    """Update project as accepted for processing"""
    is_staff_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.is_draft = False
        project.updated_on = timezone.now()
        project.save()
    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_delete(request, project_id=None):
    """Mark project as deleted in the DB"""
    is_staff_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.deleted = project.updated_on = timezone.now()
        project.save()
    return redirect(reverse("projects-project-list"))


class ProjectForm(forms.ModelForm):
    """Form for updating the base information of a project"""

    class Meta:
        model = models.Project
        fields = [
            "email",
            "first_name",
            "last_name",
            "org_name",
            "name",
            "location",
            "description",
            "impediments",
        ]


@login_required
def create_note(request, project_id=None):
    """Create a new note for a project"""
    is_staff_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.project = project
            instance.save()
            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        form = NoteForm()
    return render(request, "projects/project/note.html", locals())


@login_required
def update_note(request, note_id=None):
    """Update an existing note for a project"""
    is_staff_or_403(request.user)
    note = get_object_or_404(models.Note, pk=note_id)
    project = note.project  # For template consistency

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_on = timezone.now()
            instance.save()
            instance.project.updated_on = instance.updated_on
            instance.project.save()
            return redirect(reverse("projects-project-detail", args=[note.project_id]))
    else:
        form = NoteForm(instance=note)
    return render(request, "projects/project/note.html", locals())


class NoteForm(forms.ModelForm):
    """Form new project note creation"""

    class Meta:
        model = models.Note
        fields = ["content", "tags", "public"]

    content = MarkdownxFormField()


@login_required
def create_task(request, project_id=None):
    """Create a new task for a project"""
    is_staff_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.project = project
            instance.save()
            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        form = TaskForm()
    return render(request, "projects/project/task_create.html", locals())


@login_required
def update_task(request, task_id=None):
    """Update an existing task for a project"""
    is_staff_or_403(request.user)
    task = get_object_or_404(models.Task, pk=task_id)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_on = timezone.now()
            instance.save()
            instance.project.updated_on = instance.updated_on
            instance.project.save()
            return redirect(reverse("projects-project-detail", args=[task.project_id]))
    else:
        form = TaskForm(instance=task)
    return render(request, "projects/project/task_update.html", locals())


class TaskForm(forms.ModelForm):
    """Form new project task creation"""

    class Meta:
        model = models.Task
        fields = [
            "intent",
            "content",
            "tags",
            "public",
            "deadline",
            "resource",
            "contact",
            "done",
        ]


########################################################################
# push resource to project
########################################################################


@login_required
def push_resource(request, project_id=None):
    """Start the process of pushing a resource to given project"""
    is_staff_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        request.session["project_id"] = project.id
        return redirect(reverse("resources-resource-search"))
    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def create_resource_action(request, resource_id=None):
    """Create action for given resource to project stored in session"""
    is_staff_or_403(request.user)
    project_id = request.session.get("project_id")
    resource = get_object_or_404(resources.Resource, pk=resource_id)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        form = ResourceTaskForm(request.POST)
        if form.is_valid():
            # create a new bookmark with provided information
            task = form.save(commit=False)
            task.project = project
            task.resource = resource
            task.created_by = request.user
            task.save()
            # cleanup the session
            del request.session["project_id"]

            # Send notifications
            if form.cleaned_data["notify_email"]:
                send_email(
                    request,
                    user_email=project.email,
                    email_subject="[{0}] UrbanVitaliz vous propose une action".format(
                        project.name
                    ),
                    template_base_name="projects/notifications/task_new_email",
                    extra_context={
                        "task": task,
                        "project": project,
                        "resource": resource,
                    },
                )

                messages.success(
                    request,
                    '{0} a été notifié(e) par courriel de l\'action "{1}".'.format(
                        project.full_name, task.intent
                    ),
                    extra_tags=["email"],
                )

            next_url = reverse("projects-project-detail", args=[project.id])
            return redirect(next_url)
    else:
        form = ResourceTaskForm()
    return render(request, "projects/project/push.html", locals())


class ResourceTaskForm(forms.ModelForm):
    """Create and task for push resource"""

    notify_email = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = models.Task
        fields = ["intent", "content", "contact", "notify_email"]


########################################################################
# RSS Feeds
########################################################################


class LatestProjectsFeed(Feed):
    title = "Derniers projets"
    link = "/projects/feed"
    description = "Derniers ajouts de projets"

    def items(self):
        return models.Project.objects.order_by("-created_on")[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse("projects-project-detail", args=[item.pk])

    def item_pubdate(self, item):
        return item.created_on


# eof
