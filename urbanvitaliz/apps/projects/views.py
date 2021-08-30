# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from markdownx.fields import MarkdownxFormField

from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.resources import models as resources

from urbanvitaliz.utils import is_staff_or_403, send_email

from . import models

########################################################################
# notifications
########################################################################


def notify_action_created(request, project, task, resource=None):
    """
    Notify the creation of an Action the user by sending an email and displaying
    a UI popup
    """
    # TODO send to all project emails
    send_email(
        request,
        user_email=project.email,
        email_subject="[{0}] UrbanVitaliz vous propose une action".format(project.name),
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
            response = redirect("projects-project-detail", project_id=project.id)
            response["Location"] += "?first_time=1"
            return response
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
    if request.user.email not in project.emails:
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
            postcode = form.cleaned_data.get("postcode")
            project.commune = geomatics.Commune.get_by_postal_code(postcode)
            instance.updated_on = timezone.now()
            instance.save()
            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        if project.commune:
            postcode = project.commune.postal
        else:
            postcode = None
        form = ProjectForm(instance=project, initial={"postcode": postcode})
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

    postcode = forms.CharField(max_length=5, required=False, label="Code Postal")

    class Meta:
        model = models.Project
        fields = [
            "email",
            "first_name",
            "last_name",
            "org_name",
            "name",
            "postcode",
            "location",
            "description",
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
    return render(request, "projects/project/note_create.html", locals())


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
    return render(request, "projects/project/note_update.html", locals())


@login_required
def delete_note(request, note_id=None):
    """Delete existing note for a project"""
    is_staff_or_403(request.user)
    note = get_object_or_404(models.Note, pk=note_id)

    if request.method == "POST":
        note.updated_on = timezone.now()
        note.deleted = timezone.now()
        note.save()
        note.project.updated_on = note.updated_on
        note.project.save()

    return redirect(reverse("projects-project-detail", args=[note.project_id]))


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
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.project = project
            instance.save()

            # Send notifications
            if form.cleaned_data["notify_email"]:
                notify_action_created(request, project, task=instance)

            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        form = CreateTaskForm()
    return render(request, "projects/project/task_create.html", locals())


@login_required
def update_task(request, task_id=None):
    """Update an existing task for a project"""
    is_staff_or_403(request.user)
    task = get_object_or_404(models.Task, pk=task_id)
    if request.method == "POST":
        form = UpdateTaskForm(request.POST, instance=task)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_on = timezone.now()
            instance.save()
            instance.project.updated_on = instance.updated_on
            instance.project.save()
            return redirect(reverse("projects-project-detail", args=[task.project_id]))
    else:
        form = UpdateTaskForm(instance=task)
    return render(request, "projects/project/task_update.html", locals())


class CreateTaskForm(forms.ModelForm):
    """Form new project task creation"""

    content = MarkdownxFormField(required=False)

    notify_email = forms.BooleanField(initial=True, required=False)

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
            "notify_email",
        ]


class UpdateTaskForm(forms.ModelForm):
    """Form for task update"""

    content = MarkdownxFormField(required=False)

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


@login_required
def delete_task(request, task_id=None):
    """Delete a task from a project"""
    is_staff_or_403(request.user)
    task = get_object_or_404(models.Task, pk=task_id)
    if request.method == "POST":
        task.deleted = timezone.now()
        task.save()
    next_url = reverse("projects-project-detail", args=[task.project_id])
    return redirect(next_url)


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
                notify_action_created(request, project, task, resource)

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
