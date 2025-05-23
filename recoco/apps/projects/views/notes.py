# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

import notifications
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.text import slugify

from recoco.apps.addressbook.models import Contact
from recoco.utils import has_perm, has_perm_or_403

from .. import models, signals
from ..forms import DocumentUploadForm, NoteForm, PublicNoteForm, StaffNoteForm
from ..utils import can_administrate_project, get_collaborators_for_project


@login_required
def create_public_note(request, project_id=None):
    """Create a new note for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    has_perm_or_403(request.user, "projects.use_public_notes", project)

    if request.method == "POST":
        form = PublicNoteForm(request.POST)
        form.set_contact_queryset(
            Contact.objects.filter(site_id=request.site.id),
        )

        if form.is_valid():
            instance = form.save(commit=False)

            instance.project = project
            instance.created_by = request.user
            instance.site = request.site
            instance.public = True

            topic_name = form.cleaned_data.get("topic_name", None)
            if topic_name:
                try:
                    instance.topic = models.Topic.objects.get(
                        site__in=project.sites.all(), name__iexact=topic_name
                    )
                except models.Topic.DoesNotExist:
                    return HttpResponseBadRequest("Topic unknown")

            instance.save()

            # Check if we have a file or link
            document_form = DocumentUploadForm(request.POST, request.FILES)
            if document_form.is_valid():
                if document_form.cleaned_data["the_file"]:
                    document = document_form.save(commit=False)
                    document.attached_object = instance
                    document.site = request.site
                    document.uploaded_by = request.user
                    document.project = instance.project

                    document.save()

            # Reactivate project if was set inactive
            if request.user in get_collaborators_for_project(project):
                project.last_members_activity_at = timezone.now()

                if project.inactive_since:
                    project.reactivate()

                project.save()

            signals.note_created.send(
                sender=create_public_note,
                note=instance,
                project=project,
                user=request.user,
            )

    if request.POST.get("new", None):
        url = reverse("projects-project-detail-conversations-new", args=[project_id])
        return redirect(
            f"{url}?{urlencode({'topic-slug': slugify(topic_name or 'general'), 'topic-name': topic_name})}"
        )

    return redirect(reverse("projects-project-detail-conversations", args=[project_id]))


@login_required
def create_private_note(request, project_id=None):
    """Create a new private note for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    has_perm_or_403(request.user, "projects.use_private_notes", project)

    is_advisor = can_administrate_project(project, request.user)

    if request.method == "POST":
        form = NoteForm(request.POST)

        form.set_contact_queryset(
            Contact.objects.filter(site_id=request.site.id),
        )

        if form.is_valid():
            instance = form.save(commit=False)
            instance.project = project
            instance.created_by = request.user
            instance.site = request.site

            instance.save()

            signals.note_created.send(
                sender=create_private_note,
                note=instance,
                project=project,
                user=request.user,
            )

            return redirect(
                reverse("projects-project-detail-internal-followup", args=[project_id])
            )
    else:
        form = NoteForm()
    return render(request, "projects/project/note_create.html", locals())


@login_required
def update_note(request, note_id=None):
    """Update an existing note for a project"""
    note = get_object_or_404(models.Note, pk=note_id, site=request.site)
    project = note.project  # For template consistency

    is_advisor = can_administrate_project(project, request.user)

    if not note.public:
        is_my_note = note.created_by == request.user
        if not (
            is_my_note and has_perm(request.user, "projects.use_private_notes", project)
        ):
            raise PermissionDenied("Vous n'avez pas de le droit de modifier cette note")
    else:
        has_perm_or_403(request.user, "projects.use_public_notes", project)

    if request.method == "POST":
        if is_advisor:
            form = StaffNoteForm(request.POST, instance=note)

        else:
            form = NoteForm(request.POST, instance=note)

        form.set_contact_queryset(
            Contact.objects.filter(site_id=request.site.id),
        )
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_on = timezone.now()
            instance.save()
            instance.project.updated_on = instance.updated_on
            instance.project.save()
            if instance.public:
                return redirect(
                    reverse(
                        "projects-project-detail-conversations", args=[note.project_id]
                    )
                )

            return redirect(
                reverse(
                    "projects-project-detail-internal-followup", args=[note.project_id]
                )
            )
    else:
        if is_advisor:
            form = StaffNoteForm(instance=note)
        else:
            form = NoteForm(instance=note)
    return render(request, "projects/project/note_update.html", locals())


@login_required
def delete_note(request, note_id=None):
    """Delete existing note for a project"""
    note = get_object_or_404(models.Note, pk=note_id, site=request.site)

    if note.public and note.created_by == request.user:
        has_perm_or_403(request.user, "projects.use_public_notes", note.project)
    else:
        has_perm_or_403(request.user, "projects.use_private_notes", note.project)

    if request.method == "POST":
        note.updated_on = timezone.now()
        note.deleted = timezone.now()
        note.save()
        note.project.updated_on = note.updated_on
        note.project.save()

        cleanup_notifications_for_note(note)

        if note.public:
            return redirect(
                reverse("projects-project-detail-conversations", args=[note.project_id])
            )

    return redirect(
        reverse("projects-project-detail-internal-followup", args=[note.project_id])
    )


# This functions could be made more general
def cleanup_notifications_for_note(note):
    """Delete all notifications related to this note"""
    note_ct = ContentType.objects.get_for_model(models.Note)
    notifications.models.Notification.objects.filter(
        action_object_content_type=note_ct,
        action_object_object_id=note.id,
    ).delete()


# eof
