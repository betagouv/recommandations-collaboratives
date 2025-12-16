# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-03-07 15:56:20 CEST -- HB David!
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from recoco import verbs
from recoco.apps.hitcount.models import HitCount
from recoco.apps.invites.forms import InviteForm
from recoco.apps.survey import models as survey_models
from recoco.utils import has_perm, has_perm_or_403, is_staff_for_site

from .. import models
from ..forms import (
    PrivateNoteForm,
    ProjectLocationForm,
    ProjectTagsForm,
    ProjectTopicsForm,
    TopicForm,
)
from ..utils import (
    get_advising_context_for_project,
    get_notification_recipients_for_project,
    is_advisor_for_project,
    is_member,
    is_regional_actor_for_project,
)


@login_required
def project_detail(request, project_id=None):
    """Set as active project, then redirect to overview page"""
    return redirect(reverse("projects-project-detail-overview", args=[project_id]))


@login_required
def project_overview(request, project_id=None):
    """Return the details of given project for switchtender"""

    project = get_object_or_404(
        models.Project.objects.filter(sites=request.site)
        .with_unread_notifications(user_id=request.user.id)
        .select_related("commune__department"),
        pk=project_id,
    )

    site_config = request.site_config

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    users_to_display = list(
        HitCount.on_site.for_context_object(project)
        .for_user(request.user)
        .filter(
            content_object_ct=ContentType.objects.get_for_model(User),
        )
        .distinct()
        .values_list("content_object_id", flat=True)
    )

    advising, advising_position = get_advising_context_for_project(
        request.user, project
    )

    has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
        request.user, "view_project", project
    )

    try:
        onboarding_response = dict(project.onboarding.response)
    except models.Project.onboarding.RelatedObjectDoesNotExist:
        onboarding_response = None

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
        # verbs.Conversation.PUBLIC_MESSAGE,
        # verbs.Document.ADDED,  # FIXME to remove
        # verbs.Document.ADDED_FILE,
        # verbs.Document.ADDED_LINK,
        verbs.Project.BECAME_SWITCHTENDER,
        verbs.Project.BECAME_ADVISOR,
        verbs.Project.BECAME_OBSERVER,
        verbs.Project.JOINED,
        verbs.Project.SUBMITTED_BY,
        verbs.Project.VALIDATED,
        verbs.Project.VALIDATED_BY,
        verbs.Project.SET_INACTIVE,
        verbs.Project.SET_ACTIVE,
        # verbs.Recommendation.COMMENTED,
        # verbs.Survey.UPDATED,
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

    project = get_object_or_404(
        models.Project.objects.filter(sites=request.site)
        .with_unread_notifications(user_id=request.user.id)
        .select_related("commune__department"),
        pk=project_id,
    )

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    advising, advising_position = get_advising_context_for_project(
        request.user, project
    )

    can_view_updated_answers = (
        advising
        or is_member(request.user, project, allow_draft=True)
        or is_staff_for_site(request.user, request.site)
    )

    has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
        request.user, "view_surveys", project
    )

    site_config = request.site_config

    session, created = survey_models.Session.objects.get_or_create(
        project=project, survey=site_config.project_survey
    )

    sorted_sessions = sorted(
        project.survey_session.select_related("survey__site"),
        key=lambda session: session.survey.site != request.site,
    )

    # Mark this project survey notifications as read
    if not request.user.is_hijacked:
        project_ct = ContentType.objects.get_for_model(project)
        survey_ct = ContentType.objects.get_for_model(survey_models.Session)
        request.user.notifications.unread().filter(
            action_object_content_type=survey_ct,
            target_content_type=project_ct.pk,
            target_object_id=project.pk,
        ).mark_all_as_read()

    return render(request, "projects/project/knowledge.html", locals())


@login_required
def project_actions(request, project_id=None):
    """Action page for given project"""

    project = get_object_or_404(
        models.Project.objects.filter(sites=request.site)
        .with_unread_notifications(user_id=request.user.id)
        .select_related("commune__department"),
        pk=project_id,
    )

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    advising, advising_position = get_advising_context_for_project(
        request.user, project
    )

    has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
        request.user, "view_tasks", project
    )

    # FIXME check this really been deleted from develop
    # Mark this project action notifications as read
    # project_ct = ContentType.objects.get_for_model(project)
    # task_ct = ContentType.objects.get_for_model(task_models.Task)
    # task_notifications = request.user.notifications.unread().filter(
    #     action_object_content_type=task_ct,
    #     target_content_type=project_ct.pk,
    #     target_object_id=project.pk,
    # )  # XXX Bug?

    return render(request, "projects/project/actions.html", locals())


@xframe_options_exempt
@csrf_exempt
def project_recommendations_embed(request, project_id=None):
    """Embed recommendation page for given project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    key = request.GET.get("key", None)
    if not key or key != project.ro_key:
        return HttpResponseForbidden()

    actions = project.tasks.filter(public=True).order_by("-created_on", "-updated_on")

    return render(request, "projects/project/actions_embed.html", locals())


@login_required
def project_actions_inline(request, project_id=None):
    """Inline Action page for given project"""

    project = get_object_or_404(
        models.Project.objects.select_related("commune__department"),
        sites=request.site,
        pk=project_id,
    )

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    advising, advising_position = get_advising_context_for_project(
        request.user, project
    )

    has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
        request.user, "view_tasks", project
    )

    return render(request, "projects/project/actions_inline.html", locals())


@login_required
def project_conversations_new(request, project_id=None):
    """New Conversation page for project"""

    project = get_object_or_404(
        models.Project.objects.filter(sites=request.site)
        .with_unread_notifications(user_id=request.user.id)
        .select_related("commune__department"),
        pk=project_id,
    )

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    is_regional_actor or has_perm_or_403(request.user, "view_public_notes", project)

    advising, advising_position = get_advising_context_for_project(
        request.user, project
    )

    recipients = get_notification_recipients_for_project(project)

    # Convert QuerySet to list of dicts for JSON serialization
    recipients_data = list(
        recipients.values(
            "id",
            "email",
            "first_name",
            "last_name",
            "profile__organization__name",
            "profile__organization_position",
            "is_active",
        )
    )

    return render(
        request,
        "projects/project/conversations_new.html",
        context={
            "project": project,
            "is_regional_actor": is_regional_actor,
            "advising": advising,
            "advising_position": advising_position,
            "recipients": recipients_data,
        },
    )


@login_required
def project_internal_followup(request, project_id=None):
    """Advisors chat for given project"""

    project = get_object_or_404(
        models.Project.objects.filter(sites=request.site).with_unread_notifications(
            user_id=request.user.id
        ),
        pk=project_id,
    )

    has_perm_or_403(request.user, "projects.use_private_notes", project)

    advising, advising_position = get_advising_context_for_project(
        request.user, project
    )

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

    advising, advising_position = get_advising_context_for_project(
        request.user, project
    )

    return render(request, "projects/project/internal_followup_tracking.html", locals())


@login_required
def project_create_or_update_topics(request, project_id=None):
    """Create/Update topics for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    advising, advising_position = get_advising_context_for_project(
        request.user, project
    )

    has_perm_or_403(request.user, "projects.change_topics", project)

    TopicFormset = formset_factory(TopicForm, extra=4, max_num=4, can_delete=True)

    if request.method == "POST":
        topic_formset = TopicFormset(request.POST)
        form = ProjectTopicsForm(request.POST, instance=project)
        if form.is_valid() and topic_formset.is_valid():
            project = form.save(commit=False)
            project.advisors_note_on = timezone.now()
            project.advisors_note_by = request.user
            project.save()
            form.save_m2m()

            # Handle topics
            # Add new ones to project or removed deleted ones.
            project.topics.clear()

            for tform in topic_formset:
                name = tform.cleaned_data.get("name")
                to_remove = tform.cleaned_data.get("DELETE", False)

                if not name or to_remove:
                    continue  # no data in form,just skip it

                topic, _ = models.Topic.objects.get_or_create(
                    site=request.site,
                    name__iexact=name.lower(),
                    defaults={"name": name.capitalize(), "site": request.site},
                )
                project.topics.add(topic)

            return redirect(
                reverse("projects-project-detail-overview", args=[project.pk])
            )
    else:
        topics = [{"name": t.name} for t in project.topics.all()]
        topic_formset = TopicFormset(initial=topics)
        form = ProjectTopicsForm(instance=project)

    return render(request, "projects/project/topics.html", locals())


def project_update_tags(request, project_id=None):
    """Create/Update tags for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    advising, advising_position = get_advising_context_for_project(
        request.user, project
    )

    has_perm_or_403(request.user, "projects.use_project_tags", project)

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


###########################################################################
# Geolocation
###########################################################################


def project_update_location(request, project_id=None):
    """Fill/update geolocation for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    has_perm_or_403(request.user, "projects.change_location", project)

    if request.method == "POST":
        form = ProjectLocationForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()

            next_url = request.GET.get("next", None)
            if next_url:
                return redirect(next_url)

            return redirect(
                reverse("projects-project-detail-overview", args=[project.pk])
            )
    else:
        form = ProjectLocationForm(instance=project)

    return render(request, "projects/project/location.html", locals())


# eof
