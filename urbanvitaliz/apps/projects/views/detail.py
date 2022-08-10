# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-03-07 15:56:20 CEST -- HB David!
"""

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, reverse
from urbanvitaliz.apps.survey import models as survey_models
from urbanvitaliz.utils import check_if_switchtender, get_site_config_or_503

from .. import models
from ..forms import PrivateNoteForm, PublicNoteForm
from ..utils import (can_administrate_or_403, can_administrate_project,
                     can_manage_or_403, can_manage_project,
                     check_if_national_actor,
                     get_notification_recipients_for_project,
                     is_regional_actor_for_project, set_active_project_id)


@login_required
def project_detail(request, project_id=None):
    """Set as active project, then redirect to knowledge page"""
    return redirect(reverse("projects-project-detail-knowledge", args=[project_id]))


@login_required
def project_knowledge(request, project_id=None):
    """Return the details of given project for switchtender"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_national_actor = check_if_national_actor(request.user)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    can_administrate = can_administrate_project(project, request.user)

    # check user can administrate project (member or switchtender)
    if request.user != project.members.filter(projectmember__is_owner=True).first():
        # bypass if user is switchtender, all are allowed to view at least
        if not check_if_switchtender(request.user):
            can_manage_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    site_config = get_site_config_or_503(request.site)
    session, created = survey_models.Session.objects.get_or_create(
        project=project, survey=site_config.project_survey
    )

    # Mark some notifications as seen (general ones)
    project_ct = ContentType.objects.get_for_model(project)
    general_notifications = request.user.notifications.unread().filter(
        Q(verb="est devenu·e aiguilleur·se sur le projet")
        | Q(verb="a été validé")
        | Q(verb="a validé le projet")
        | Q(verb="a soumis pour modération le projet")
        | Q(verb="a mis à jour le questionnaire")
        | Q(verb="a ajouté un document")
        | Q(verb="a envoyé un message")
        | Q(verb="a rejoint l'équipe sur le projet"),
        target_content_type=project_ct.pk,
        target_object_id=project.pk,
    )

    general_notifications.mark_all_as_read()

    return render(request, "projects/project/knowledge.html", locals())


@login_required
def project_actions(request, project_id=None):
    """Action page for given project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_national_actor = check_if_national_actor(request.user)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    can_administrate = can_administrate_project(project, request.user)

    # check user can administrate project (member or switchtender)
    if request.user != project.members.filter(projectmember__is_owner=True).first():
        # bypass if user is switchtender, all are allowed to view at least
        if not check_if_switchtender(request.user):
            can_manage_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    # Mark this project action notifications as read
    project_ct = ContentType.objects.get_for_model(project)
    task_ct = ContentType.objects.get_for_model(models.Task)
    task_notifications = request.user.notifications.unread().filter(
        action_object_content_type=task_ct,
        target_content_type=project_ct.pk,
        target_object_id=project.pk,
    )

    return render(request, "projects/project/actions.html", locals())


@login_required
def project_conversations(request, project_id=None):
    """Action page for given project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_national_actor = check_if_national_actor(request.user)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    can_administrate = can_administrate_project(project, request.user)

    # check user can administrate project (member or switchtender)
    if request.user != project.members.filter(projectmember__is_owner=True).first():
        # bypass if user is switchtender, all are allowed to view at least
        if not check_if_switchtender(request.user):
            can_manage_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    public_note_form = PublicNoteForm()

    recipients = get_notification_recipients_for_project(project)

    # Mark this project notifications as read
    project_ct = ContentType.objects.get_for_model(project)
    note_ct = ContentType.objects.get_for_model(models.Note)
    request.user.notifications.unread().filter(
        action_object_content_type=note_ct,
        action_notes__public=True,
        target_content_type=project_ct.pk,
        target_object_id=project.pk,
    ).mark_all_as_read()

    return render(request, "projects/project/conversations.html", locals())


@login_required
def project_internal_followup(request, project_id=None):
    """Action page for given project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    can_administrate_or_403(project, request.user)

    # compute permissions
    can_manage = can_manage_project(project, request.user)
    can_manage_draft = can_manage_project(project, request.user, allow_draft=True)
    is_regional_actor = is_regional_actor_for_project(
        project, request.user, allow_national=True
    )
    is_national_actor = check_if_national_actor(request.user)
    can_administrate = can_administrate_project(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    # Mark this project notifications as read
    project_ct = ContentType.objects.get_for_model(project)
    note_ct = ContentType.objects.get_for_model(models.Note)
    request.user.notifications.unread().filter(
        action_object_content_type=note_ct,
        action_notes__public=False,
        target_content_type=project_ct.pk,
        target_object_id=project.pk,
    ).mark_all_as_read()

    private_note_form = PrivateNoteForm()

    return render(request, "projects/project/internal_followup.html", locals())
