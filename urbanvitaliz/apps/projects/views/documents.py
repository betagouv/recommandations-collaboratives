# encoding: utf-8

"""
Views for projects application

author  : guillaume.libersat@beta.gouv.fr
created : 2022-11-28 14:14:20 CEST 
"""

from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from urbanvitaliz.utils import check_if_advisor, has_perm_or_403

from .. import models, signals
from ..forms import DocumentUploadForm
from ..utils import (
    can_administrate_project,
    can_manage_project,
    check_if_national_actor,
    get_switchtender_for_project,
    is_regional_actor_for_project,
    set_active_project_id,
)


@login_required
def document_list(request, project_id=None):
    """Manage files and links for project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    has_perm_or_403(request.user, "manage_documents", project)

    # Set this project as active
    set_active_project_id(request, project.pk)

    all_files = models.Document.on_site.filter(project_id=project.pk).exclude(
        the_file__in=["", None]
    )
    pinned_files = all_files.filter(pinned=True)
    links = models.Document.on_site.filter(project_id=project.pk).exclude(the_link=None)

    return render(request, "projects/project/documents.html", locals())


@login_required
def document_upload(request, project_id):
    """Upload a new document for a project"""
    project = get_object_or_404(models.Project, pk=project_id, sites=request.site)

    has_perm_or_403(request.user, "manage_documents", project)

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.project = project
            instance.site = request.site
            instance.uploaded_by = request.user

            try:
                instance.save()

                signals.document_uploaded.send(
                    sender=document_upload, instance=instance
                )

                messages.success(
                    request,
                    "Le document a bien été enregistré",
                )

            except IntegrityError:
                messages.error(request, "Impossible de sauver le document")

    return redirect(reverse("projects-project-detail-documents", args=[project.id]))


@login_required
def document_delete(request, project_id, document_id):
    """Delete a document for a project"""
    project = get_object_or_404(models.Project, pk=project_id, sites=request.site)
    document = get_object_or_404(models.Document, pk=document_id, site=request.site)

    has_perm_or_403(request.user, "manage_documents", project)

    if request.method == "POST":
        if document.uploaded_by != request.user:
            raise PermissionDenied()

        document.deleted = timezone.now()
        document.save()
        messages.success(
            request,
            "Le document a bien été supprimé",
        )

    return redirect(reverse("projects-project-detail-documents", args=[project.id]))


@login_required
def document_pin_unpin(request, project_id, document_id):
    """Delete a document for a project"""
    project = get_object_or_404(models.Project, pk=project_id, sites=request.site)
    document = get_object_or_404(models.Document, pk=document_id, site=request.site)

    has_perm_or_403(request.user, "manage_documents", project)

    if request.method == "POST":
        document.pinned = not document.pinned
        document.save()

    return redirect(reverse("projects-project-detail-documents", args=[project.id]))
