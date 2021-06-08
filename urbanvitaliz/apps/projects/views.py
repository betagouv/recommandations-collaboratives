# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django.contrib.auth.decorators import login_required

from django import forms

from django.urls import reverse

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

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
            "name",
            "location",
            "description",
            "impediments",
        ]


########################################################################
# Local authorities
########################################################################


@login_required
def local_authorities(request):
    """Return the project followup for local authorities"""
    projects = models.Project.fetch(email=request.user.email)
    return render(request, "projects/collectivite.html", locals())


########################################################################
# Switchtender
########################################################################


@login_required
def project_list(request):
    """Return the projects for the switchtender"""
    projects = models.Project.fetch().order_by("-created_on")
    return render(request, "projects/project/list.html", locals())


@login_required
def project_detail(request, project_id=None):
    """Return the details of given project for switchtender"""
    project = get_object_or_404(models.Project, pk=project_id)
    return render(request, "projects/project/detail.html", locals())


@login_required
def create_note(request, project_id=None):
    """Create a new note for a project"""
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


class NoteForm(forms.ModelForm):
    """Form new project note creation"""

    class Meta:
        model = models.Note
        fields = ["content", "tags", "public"]


@login_required
def create_task(request, project_id=None):
    """Create a new task for a project"""
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


class TaskForm(forms.ModelForm):
    """Form new project task creation"""

    class Meta:
        model = models.Task
        fields = ["content", "tags", "public", "deadline"]


# eof
