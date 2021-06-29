# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django.contrib.auth.decorators import login_required

from django import forms

from django.urls import reverse

from django.contrib.syndication.views import Feed
from django.utils import timezone

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from markdownx.fields import MarkdownxFormField

from urbanvitaliz.utils import is_staff_or_403

from . import models


########################################################################
# On boarding
########################################################################


def onboarding(request):
    """Return the onboarding page"""
    if request.method == "POST":
        form = OnboardingForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return render(request, "projects/thanks.html", locals())
    else:
        form = OnboardingForm()
    return render(request, "projects/onboarding.html", locals())


class OnboardingForm(forms.ModelForm):
    """Form for onboarding a new local authority"""

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
    """Return the projects followup for local authorities"""
    projects = models.Project.fetch(email=request.user.email)
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
    return render(request, "projects/project/task.html", locals())


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
    return render(request, "projects/project/task.html", locals())


class TaskForm(forms.ModelForm):
    """Form new project task creation"""

    class Meta:
        model = models.Task
        fields = ["content", "tags", "public", "deadline", "done"]


@login_required
def push_resource(request, project_id=None):
    """Start the process of pushing a resource to given project"""
    is_staff_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        request.session["project_id"] = project.id
        return redirect(reverse("resources-resource-search"))
    return redirect(reverse("projects-project-detail", args=[project_id]))


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


# eof
