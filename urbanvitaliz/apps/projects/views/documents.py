# encoding: utf-8

"""
Views for projects application

author  : guillaume.libersat@beta.gouv.fr
created : 2022-11-28 14:14:20 CEST 
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from urbanvitaliz.utils import check_if_switchtender

from .. import models
from ..forms import DocumentUploadForm
from ..utils import (can_administrate_project, can_manage_or_403,
                     can_manage_project, check_if_national_actor,
                     get_switchtender_for_project,
                     is_regional_actor_for_project, set_active_project_id)


@login_required
def document_list(request, project_id=None):
    """Manage files and links for project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_national_actor = check_if_national_actor(request.user)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    can_administrate = can_administrate_project(project, request.user)
    switchtending = get_switchtender_for_project(request.user, project)

    # check user can administrate project (member or switchtender)
    if request.user != project.members.filter(projectmember__is_owner=True).first():
        # bypass if user is switchtender, all are allowed to view at least
        if not check_if_switchtender(request.user):
            can_manage_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    files = models.Document.on_site.filter(project_id=project.pk)
    links = models.Document.on_site.filter(project_id=project.pk)

    return render(request, "projects/project/files_links.html", locals())


@login_required
def document_upload(request, project_id):
    """Upload a new document for a project"""
    project = get_object_or_404(models.Project, pk=project_id, sites=request.site)
    can_manage_or_403(project, request.user)

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.project = project
            instance.site = request.site
            instance.uploaded_by = request.user

            instance.save()

            messages.success(
                request,
                "Le document a bien été enregistré",
            )

    return redirect(reverse("projects-project-detail-documents", args=[project.id]))


@login_required
def document_delete(request, project_id, document_id):
    """Delete a document for a project"""
    project = get_object_or_404(models.Project, pk=project_id, sites=request.site)
    document = get_object_or_404(models.Document, pk=document_id, site=request.site)

    can_manage_or_403(project, request.user)

    if request.method == "POST":
        if document.uploaded_by == request.user:
            document.deleted = timezone.now()
            document.save()
            messages.success(
                request,
                "Le document a bien été supprimé",
            )

        else:
            raise PermissionDenied()

    return redirect(reverse("projects-project-detail-documents", args=[project.id]))
