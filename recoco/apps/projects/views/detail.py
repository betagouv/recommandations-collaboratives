# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-03-07 15:56:20 CEST -- HB David!
"""

from datetime import timedelta
from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from recoco import verbs
from recoco.apps.addressbook.models import Contact
from recoco.apps.conversations import api as conversations_api
from recoco.apps.hitcount.models import HitCount
from recoco.apps.invites.forms import InviteForm
from recoco.apps.projects.views.notes import create_public_note
from recoco.apps.survey import models as survey_models
from recoco.apps.tasks import models as tasks_models
from recoco.utils import has_perm, has_perm_or_403, is_staff_for_site, require_htmx

from .. import models, signals
from ..forms import (
    DocumentUploadForm,
    PrivateNoteForm,
    ProjectLocationForm,
    ProjectTagsForm,
    ProjectTopicsForm,
    PublicNoteForm,
    TopicForm,
)
from ..utils import (
    get_advising_context_for_project,
    get_collaborators_for_project,
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
def project_conversations(request, project_id=None):
    """Conversation page for project"""

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

    is_regional_actor or has_perm_or_403(request.user, "view_public_notes", project)

    public_note_form = PublicNoteForm()
    public_note_form.set_contact_queryset(
        Contact.objects.filter(site_id=request.site.id)
    )

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


def _build_feeds(project: models.Project, user: User) -> list[dict[str, Any]]:
    # Prepare a feed of different objects
    feed = []

    def feed_add_item(timestamp, topic, item_type, notifications, related_object):
        feed.append(
            {
                "timestamp": timestamp,
                "topic": topic,
                "type": item_type,
                "notifications": notifications,
                "object": related_object,
            }
        )

    feed_object_templates = [
        (
            "posting",  # feed item type
            models.Note,  # model
            project.notes.filter(public=True),  # initial queryset
            lambda item: item.updated_on,  # timestamp
            # lambda item: item.topic.name if item.topic else "",  # topic
            lambda item: "",
        ),
        (
            "reco",
            tasks_models.Task,
            project.tasks.filter(public=True),
            lambda item: item.updated_on,
            # lambda item: item.topic.name if item.topic else "",
            lambda item: "",
        ),
        (
            "followup",
            tasks_models.TaskFollowup,
            tasks_models.TaskFollowup.objects.filter(
                task__in=project.tasks.filter(public=True)
            ),
            lambda item: item.timestamp,
            # lambda item: item.task.topic.name if item.task.topic else "",
            lambda item: "",
        ),
    ]

    for (
        item_type,
        model_instance,
        queryset,
        ts_lambda,
        topic_lambda,
    ) in feed_object_templates:
        object_ids = list(queryset.values_list("id", flat=True))
        object_ct = ContentType.objects.get_for_model(model_instance)
        object_notifs = user.notifications.unread().filter(
            action_object_object_id__in=object_ids, action_object_content_type=object_ct
        )

        for item in queryset.all():
            feed_add_item(
                timestamp=ts_lambda(item),
                topic=topic_lambda(item),
                item_type=item_type,
                notifications=list(
                    object_notifs.filter(action_object_object_id=item.id).values_list(
                        "id", flat=True
                    )
                ),
                related_object=item,
            )

    # Activities are a special case
    activity_verbs = [verbs.Project.BECAME_OBSERVER, verbs.Project.BECAME_ADVISOR]
    activities = project.target_actions.filter(verb__in=activity_verbs)
    activity_notifs = user.notifications.unread().filter(verb__in=activity_verbs)

    for activity in activities:
        max_date = activity.timestamp + timedelta(seconds=2)
        min_date = activity.timestamp - timedelta(seconds=2)

        feed_add_item(
            timestamp=activity.timestamp,
            topic="",
            item_type="activity",
            notifications=list(
                activity_notifs.filter(
                    verb=activity.verb,
                    action_object_object_id=activity.action_object_object_id,
                    action_object_content_type=activity.action_object_content_type,
                    timestamp__lte=max_date,
                    timestamp__gte=min_date,
                ).values_list("id", flat=True)
            ),
            related_object=activity,
        )

    # Pre-sort so it's easier to use in the template
    feed.sort(key=lambda x: (x["topic"], x["timestamp"]))

    return feed


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

    posting_form = PublicNoteForm()

    recipients = get_notification_recipients_for_project(project)

    feed = {
        "feed": {
            "events": [],
            "messages": conversations_api.build_message_feed(project),
        }
    }

    return render(
        request,
        "projects/project/conversations_new.html",
        context={
            "project": project,
            "is_regional_actor": is_regional_actor,
            "advising": advising,
            "posting_form": posting_form,
            "recipients": recipients,
            "feed": feed,
        },
    )


@login_required
@require_http_methods(["POST"])
@require_htmx
def project_conversations_new_partial(request, project_id=None):
    project = get_object_or_404(
        models.Project.objects.filter(sites=request.site)
        .with_unread_notifications(user_id=request.user.id)
        .select_related("commune__department"),
        pk=project_id,
    )

    # TODO: incomplete, only for demo purpose
    # we need all that is in create_public_note
    # refacto in a service method to avoid code duplication, and complete this part
    form = PublicNoteForm(request.POST)
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

    feed = _build_feeds(project=project, user=request.user)

    return render(
        request,
        "projects/project/partials/conversations_new_partial.html",
        context={
            "project": project,
            "feed": feed,
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
