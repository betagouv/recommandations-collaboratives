# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-05-31 15:56:20 CEST
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, reverse

from .. import models
from ..forms import DocumentUploadForm
from ..utils import can_manage_or_403


@login_required
def document_upload(request, project_id=None):
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

    return redirect(reverse("projects-project-detail-conversations", args=[project.id]))
