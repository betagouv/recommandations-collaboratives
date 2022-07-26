"""
Urls for crm application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-07-20 12:27:25 CEST
"""

from actstream.models import Action, actor_stream, target_stream
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render, reverse
from urbanvitaliz.apps.addressbook.models import Organization
from urbanvitaliz.apps.projects.models import Project

from . import forms, models


@staff_member_required
def organization_details(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)

    participants = User.objects.filter(
        profile__in=organization.registered_profiles.all()
    )

    advised_projects = Project.objects.filter(switchtenders__in=participants)

    org_departments = organization.departments.all()

    unadvised_projects = Project.objects.filter(
        commune__department__in=org_departments
    ).exclude(switchtenders__in=participants)

    participant_ids = list(participants.values_list("id", flat=True))

    user_ct = ContentType.objects.get_for_model(User)

    actions = Action.objects.filter(
        actor_content_type=user_ct,
        actor_object_id__in=participant_ids,
    )

    organization_ct = ContentType.objects.get_for_model(Organization)
    try:
        note = models.Note.objects.get(
            object_id=organization.pk, content_type=organization_ct
        )
    except models.Note.DoesNotExist:
        note = None

    return render(request, "crm/organization_details.html", locals())


@staff_member_required
def user_details(request, user_id):
    crm_user = get_object_or_404(User, pk=user_id)

    actions = actor_stream(crm_user)

    user_ct = ContentType.objects.get_for_model(User)
    try:
        note = models.Note.objects.get(object_id=crm_user.pk, content_type=user_ct)
    except models.Note.DoesNotExist:
        note = None

    return render(request, "crm/user_details.html", locals())


@staff_member_required
def project_details(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    actions = target_stream(project)

    project_ct = ContentType.objects.get_for_model(Project)
    try:
        note = models.Note.objects.get(object_id=project.pk, content_type=project_ct)
    except models.Note.DoesNotExist:
        note = None

    return render(request, "crm/project_details.html", locals())


def handle_create_note_for_object(
    request, the_object, return_view_name, return_update_view_name
):
    # If a note already exists, redirect
    user_ct = ContentType.objects.get_for_model(the_object)
    try:
        existing_note = models.Note.objects.get(
            object_id=the_object.pk, content_type=user_ct
        )
        return redirect(reverse(return_update_view_name, args=(existing_note.pk,)))
    except models.Note.DoesNotExist:
        pass

    if request.method == "POST":
        form = forms.CRMNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.related = the_object
            note.created_by = request.user
            note.save()
            return redirect(reverse(return_view_name, args=(the_object.pk,)))

    else:
        form = forms.CRMNoteForm()

    return render(request, "crm/note_create.html", locals())


@staff_member_required
def create_note_for_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    return handle_create_note_for_object(
        request, user, "crm-user-details", "crm-user-note-update"
    )


@staff_member_required
def create_note_for_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    return handle_create_note_for_object(
        request, project, "crm-project-details", "crm-project-note-update"
    )


@staff_member_required
def create_note_for_organization(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)

    return handle_create_note_for_object(
        request,
        organization,
        "crm-organization-details",
        "crm-organization-note-update",
    )


def update_note_for_object(request, note, return_view_name):
    if request.method == "POST":
        form = forms.CRMNoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save()
            return redirect(reverse(return_view_name, args=(note.related.pk,)))
    else:
        form = forms.CRMNoteForm(instance=note)

    return render(request, "crm/note_update.html", locals())


@staff_member_required
def update_note_for_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_ct = ContentType.objects.get_for_model(user)
    note = get_object_or_404(models.Note, object_id=user_id, content_type=user_ct)

    return update_note_for_object(request, note, "crm-user-details")


@staff_member_required
def update_note_for_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project_ct = ContentType.objects.get_for_model(project)
    note = get_object_or_404(models.Note, object_id=project_id, content_type=project_ct)

    return update_note_for_object(request, note, "crm-project-details")


@staff_member_required
def update_note_for_organization(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    organization_ct = ContentType.objects.get_for_model(organization)
    note = get_object_or_404(
        models.Note, object_id=organization_id, content_type=organization_ct
    )

    return update_note_for_object(request, note, "crm-organization-details")
