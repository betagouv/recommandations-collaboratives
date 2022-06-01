# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-05-31 15:56:20 CEST
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import timezone

from .. import models
from ..forms import DocumentUploadForm
from ..utils import can_manage_or_403


@login_required
def document_upload(request, project_id):
    """Upload a new document for a project"""
    project = get_object_or_404(models.Project, pk=project_id)
    can_manage_or_403(project, request.user)

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.project = project
            instance.uploaded_by = request.user

            instance.save()

            messages.success(
                request,
                "Le fichier a bien été envoyé",
            )

    return redirect(reverse("projects-project-detail-conversations", args=[project.id]))


@login_required
def document_delete(request, project_id, document_id):
    """Delete a document for a project"""
    project = get_object_or_404(models.Project, pk=project_id)
    document = get_object_or_404(models.Document, pk=document_id)

    can_manage_or_403(project, request.user)

    if request.method == "POST":
        if document.uploaded_by == request.user:
            document.deleted = timezone.now()
            document.save()
            messages.success(
                request,
                "Le fichier a bien été supprimé",
            )

        else:
            raise PermissionDenied()

    return redirect(reverse("projects-project-detail-conversations", args=[project.id]))
