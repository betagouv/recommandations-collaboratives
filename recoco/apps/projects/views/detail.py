# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-03-07 15:56:20 CEST -- HB David!
"""

from actstream import action
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms import formset_factory
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView

from recoco import verbs
from recoco.apps.hitcount.models import HitCount
from recoco.apps.invites.forms import InviteForm
from recoco.apps.plugins.manager import get_tenant_hook
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
    notify_advisors_of_project,
)


@login_required
def project_detail(request, project_id=None):
    """Set as active project, then redirect to overview page"""
    return redirect(reverse("projects-project-detail-overview", args=[project_id]))


class ProjectDetailBaseView(LoginRequiredMixin, DetailView):
    """Base view to share common data/computation required by the project page templates"""

    http_method_names = ["get", "head", "options"]

    pk_url_kwarg = "project_id"
    model = models.Project
    context_object_name = "project"

    def check_permissions(self):
        return has_perm(
            self.request.user, "list_projects", self.request.site
        ) or has_perm_or_403(self.request.user, "view_project", self.object)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # we cannot use "UserPassesMixin" since we need more context than possible,
        # so call this method between the object and the context creation
        self.check_permissions()

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self):
        self.pk = self.kwargs.get(self.pk_url_kwarg)

        return get_object_or_404(
            models.Project.objects.filter(sites=self.request.site)
            .with_unread_notifications(user_id=self.request.user.id)
            .select_related("commune__department")
            .prefetch_related("project_creation_requests"),
            pk=self.pk,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        is_regional_actor = is_regional_actor_for_project(
            self.request.site, self.object, self.request.user, allow_national=True
        )

        advising, advising_position = get_advising_context_for_project(
            self.request.user, self.object
        )

        context["advising"] = advising
        context["advising_position"] = advising_position

        context["project_creation_request"] = (
            self.object.project_creation_requests.first()
        )

        context["site_config"] = self.request.site_config

        context["users_to_display"] = list(
            HitCount.on_site.for_context_object(self.object)
            .for_user(self.request.user)
            .filter(
                content_object_ct=ContentType.objects.get_for_model(User),
            )
            .distinct()
            .values_list("content_object_id", flat=True)
        )

        try:
            onboarding_response = dict(self.object.onboarding.response)
        except models.Project.onboarding.RelatedObjectDoesNotExist:
            onboarding_response = None

        context["onboarding_response"] = onboarding_response

        # Make sure we track record of user's interest for this project
        if not self.request.user.is_hijacked:
            mark_notifications_as_seen(self.request.user, self.object)

            if is_regional_actor or is_advisor_for_project(
                self.request.user, self.object
            ):
                update_user_project_status(
                    self.request.site, self.request.user, self.object
                )

        context["invite_form"] = InviteForm()

        # load plugin hook for adding tab entries
        pm = get_tenant_hook(self.request)
        context["plugin_tabs"] = pm.hook.project_tab_entries()

        return context


class ProjectOverviewView(ProjectDetailBaseView):
    """Display main info of projects (first tab in nav)"""

    template_name = "projects/project/overview.html"


class ProjectKnowledgeView(ProjectDetailBaseView):
    """Show the survey results for a given project"""

    template_name = "projects/project/knowledge.html"

    def check_permissions(self):
        return has_perm(
            self.request.user, "list_projects", self.request.site
        ) or has_perm_or_403(self.request.user, "view_surveys", self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["can_view_updated_answers"] = (
            context["advising"]
            or is_member(self.request.user, self.object, allow_draft=True)
            or is_staff_for_site(self.request.user, self.request.site)
        )

        session, created = survey_models.Session.objects.get_or_create(
            project=self.object, survey=self.request.site_config.project_survey
        )

        context["sorted_sessions"] = sorted(
            self.object.survey_session.select_related("survey__site"),
            key=lambda session: session.survey.site != self.request.site,
        )

        # Mark this project survey notifications as read
        if not self.request.user.is_hijacked:
            project_ct = ContentType.objects.get_for_model(self.object)
            survey_ct = ContentType.objects.get_for_model(survey_models.Session)
            self.request.user.notifications.unread().filter(
                action_object_content_type=survey_ct,
                target_content_type=project_ct.pk,
                target_object_id=self.object.pk,
            ).mark_all_as_read()

        return context


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
        # verbs.Document.ADDED_FILE,
        # verbs.Document.ADDED_LINK,
        verbs.Project.BECAME_SWITCHTENDER,
        verbs.Project.BECAME_ADVISOR,
        verbs.Project.BECAME_OBSERVER,
        verbs.Project.JOINED_BY_INVITATION,
        verbs.Project.JOINED_OWNER,
        verbs.Project.NEW_OWNER,
        verbs.Project.SUBMITTED_BY,
        verbs.Project.SUBMITTED_BY_ADVISOR,
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


class ProjectRecommandationsView(ProjectDetailBaseView):
    """Action page for given project"""

    template_name = "projects/project/actions.html"

    def check_permissions(self):
        return has_perm(
            self.request.user, "list_projects", self.request.site
        ) or has_perm_or_403(self.request.user, "view_tasks", self.object)


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


class ProjectConversationView(ProjectDetailBaseView):
    """Conversation page for project"""

    template_name = "projects/project/conversations_new.html"

    def check_permissions(self):
        is_regional_actor = is_regional_actor_for_project(
            self.request.site, self.object, self.request.user, allow_national=True
        )

        return is_regional_actor or has_perm_or_403(
            self.request.user, "view_public_notes", self.object
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recipients = get_notification_recipients_for_project(self.object)

        # Convert QuerySet to list of dicts for JSON serialization
        context["recipients"] = list(
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

        # Get files from EDL (État des lieux) surveys
        context["edl_files"] = list(
            survey_models.Answer.objects.filter(session__project=self.object)
            .exclude(attachment="")
            .exclude(attachment__isnull=True)
            .values("id", "attachment", "updated_on")
        )

        return context


class ProjectAdvisorConversationView(ProjectDetailBaseView):
    """Advisors chat for given project"""

    template_name = "projects/project/internal_followup.html"

    def check_permissions(self):
        return has_perm_or_403(
            self.request.user, "projects.use_private_notes", self.object
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["private_note_form"] = PrivateNoteForm()

        # Mark this project notifications as read
        if not self.request.user.is_hijacked:
            project_ct = ContentType.objects.get_for_model(self.object)
            note_ct = ContentType.objects.get_for_model(models.Note)
            self.request.user.notifications.unread().filter(
                action_object_content_type=note_ct,
                action_notes__public=False,
                target_content_type=project_ct.pk,
                target_object_id=self.object.pk,
            ).mark_all_as_read()

        return context


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
    """Create/Update topics for a project and updates advisor's note"""
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
            changed_note = "advisors_note" in form.changed_data
            if changed_note:
                project.advisors_note_on = timezone.now()
                project.advisors_note_by = request.user
            project.save()
            form.save_m2m()
            if changed_note:
                action.send(
                    sender=request.user,
                    verb=verbs.Project.UPDATE_ADVISORS_NOTE,
                    action_object=project,
                )

                notify_advisors_of_project(
                    project,
                    {
                        "sender": request.user,
                        "verb": verbs.Project.UPDATE_ADVISORS_NOTE,
                        "action_object": project,
                    },
                    exclude=request.user,
                )

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
