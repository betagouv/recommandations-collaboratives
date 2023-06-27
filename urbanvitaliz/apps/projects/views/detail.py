# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-03-07 15:56:20 CEST -- HB David!
"""

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone

from urbanvitaliz import verbs
from urbanvitaliz.apps.invites.forms import InviteForm
from urbanvitaliz.apps.survey import models as survey_models
from urbanvitaliz.utils import (
    get_site_config_or_503,
    has_perm,
    has_perm_or_403,
    is_staff_for_site,
)

from .. import models
from ..forms import PrivateNoteForm, ProjectTagsForm, ProjectTopicsForm, PublicNoteForm
from ..utils import (
    get_advisor_for_project,
    get_notification_recipients_for_project,
    is_advisor_for_project,
    is_member,
    is_regional_actor_for_project,
    set_active_project_id,
)


@login_required
def project_detail(request, project_id=None):
    """Set as active project, then redirect to overview page"""
    return redirect(reverse("projects-project-detail-overview", args=[project_id]))


@login_required
def project_overview(request, project_id=None):
    """Return the details of given project for switchtender"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    advising = get_advisor_for_project(request.user, project)

    has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
        request.user, "view_project", project
    )

    try:
        onboarding_response = dict(project.onboarding.response)
    except models.Project.onboarding.RelatedObjectDoesNotExist:
        onboarding_response = None

    # Set this project as active
    set_active_project_id(request, project.pk)

    # Make sure we track record of user's interest for this project
    if not request.user.is_hijacked:
        mark_notifications_as_seen(request.user, project)

        if is_regional_actor or is_advisor_for_project(request.user, project):
            update_user_project_status(request.site, request.user, project)

    invite_form = InviteForm()

    return render(request, "projects/project/overview.html", locals())


def update_user_project_status(site, user, project):
    pus, created = models.UserProjectStatus.objects.get_or_create(
        site=site,
        user=user,
        project=project,
        defaults={"status": "TODO"},
    )
    if not created and pus.status == "NEW":
        pus.status = "TODO"
        pus.save()


def mark_notifications_as_seen(user, project):
    # Mark some notifications as seen (general ones)
    project_ct = ContentType.objects.get_for_model(project)
    notif_verbs = [
        verbs.Conversation.PUBLIC_MESSAGE,
        verbs.Conversation.PRIVATE_MESSAGE_OLD,  # FIXME and new ones ?
        verbs.Document.ADDED,  # FIXME to remove
        verbs.Document.ADDED_FILE,
        verbs.Document.ADDED_LINK,
        verbs.Project.BECAME_SWITCHTENDER,
        verbs.Project.BECAME_ADVISOR,
        verbs.Project.BECAME_OBSERVER,
        verbs.Project.JOINED,
        verbs.Project.JOINED_OLD,
        verbs.Project.SUBMITTED_BY,
        verbs.Project.VALIDATED,
        verbs.Project.VALIDATED_BY,
        verbs.Recommendation.COMMENTED,
        verbs.Survey.UPDATED,
    ]
    notifications = user.notifications.unread().filter(
        verb__in=notif_verbs,
        target_content_type_id=project_ct.pk,
        target_object_id=project.pk,
        public=True,
    )
    notifications.mark_all_as_read()


@login_required
def project_knowledge(request, project_id=None):
    """Return the survey results for a given project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    advising = get_advisor_for_project(request.user, project)

    can_view_updated_answers = (
        advising
        or is_member(request.user, project, allow_draft=True)
        or is_staff_for_site(request.user, request.site)
    )

    has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
        request.user, "view_surveys", project
    )

    # Set this project as active
    set_active_project_id(request, project.pk)

    site_config = get_site_config_or_503(request.site)
    session, created = survey_models.Session.objects.get_or_create(
        project=project, survey=site_config.project_survey
    )

    return render(request, "projects/project/knowledge.html", locals())


@login_required
def project_actions(request, project_id=None):
    """Action page for given project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    advising = get_advisor_for_project(request.user, project)

    has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
        request.user, "view_tasks", project
    )

    # Set this project as active
    set_active_project_id(request, project.pk)

    # Mark this project action notifications as read
    project_ct = ContentType.objects.get_for_model(project)
    task_ct = ContentType.objects.get_for_model(models.Task)
    task_notifications = request.user.notifications.unread().filter(
        action_object_content_type=task_ct,
        target_content_type=project_ct.pk,
        target_object_id=project.pk,
    )  # XXX Bug?

    return render(request, "projects/project/actions.html", locals())


@login_required
def project_actions_inline(request, project_id=None):
    """Inline Action page for given project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    advising = get_advisor_for_project(request.user, project)

    has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
        request.user, "view_tasks", project
    )

    # Set this project as active
    set_active_project_id(request, project.pk)

    return render(request, "projects/project/actions_inline.html", locals())


@login_required
def project_conversations(request, project_id=None):
    """Conversation page for project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    advising = get_advisor_for_project(request.user, project)

    is_regional_actor or has_perm_or_403(request.user, "view_public_notes", project)

    # Set this project as active
    set_active_project_id(request, project.pk)

    public_note_form = PublicNoteForm()

    recipients = get_notification_recipients_for_project(project)

    # Mark this project notifications as read
    if not request.user.is_hijacked:
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
    """Advisors chat for given project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    has_perm_or_403(request.user, "projects.use_private_notes", project)

    advising = get_advisor_for_project(request.user, project)

    # Set this project as active
    set_active_project_id(request, project.pk)

    # Mark this project notifications as read
    if not request.user.is_hijacked:
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


@login_required
def project_internal_followup_tracking(request, project_id=None):
    """Advisors chat for given project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    has_perm_or_403(request.user, "projects.use_private_notes", project)

    advising = get_advisor_for_project(request.user, project)

    # Set this project as active
    set_active_project_id(request, project.pk)

    return render(request, "projects/project/internal_followup_tracking.html", locals())


@login_required
def project_create_or_update_topics(request, project_id=None):
    """Create/Update topics for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    advising = get_advisor_for_project(request.user, project)

    has_perm_or_403(request.user, "projects.change_topics", project)

    TopicFormset = modelformset_factory(
        models.ProjectTopic, fields=("label",), extra=6, max_num=6, can_delete=True
    )

    if request.method == "POST":
        topic_formset = TopicFormset(
            request.POST, queryset=project.topics_on_site.all()
        )
        form = ProjectTopicsForm(request.POST, instance=project)
        if form.is_valid() and topic_formset.is_valid():
            project = form.save(commit=False)
            project.advisors_note_on = timezone.now()
            project.advisors_note_by = request.user
            project.save()
            form.save_m2m()

            # Topics
            # save new ones
            for topic in topic_formset.save(commit=False):
                topic.project = project
                topic.site = request.site
                topic.save()

            # deleted flagged ones
            for deleted_topic in topic_formset.deleted_objects:
                deleted_topic.delete()

            return redirect(
                reverse("projects-project-detail-overview", args=[project.pk])
            )
    else:
        topic_formset = TopicFormset(queryset=project.topics_on_site.all())
        form = ProjectTopicsForm(instance=project)

    return render(request, "projects/project/topics.html", locals())


def project_update_tags(request, project_id=None):
    """Create/Update tags for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    advising = get_advisor_for_project(request.user, project)

    has_perm_or_403(request.user, "sites.use_project_tags", request.site)

    if request.method == "POST":
        form = ProjectTagsForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()

            return redirect(
                reverse("projects-project-detail-overview", args=[project.pk])
            )
    else:
        form = ProjectTagsForm(instance=project)

    return render(request, "projects/project/tags.html", locals())


# eof
