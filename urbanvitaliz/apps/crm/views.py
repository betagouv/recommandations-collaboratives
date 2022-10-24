"""
Views for crm application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-07-20 12:27:25 CEST
"""

from actstream.models import Action, actor_stream, target_stream
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.views import Feed
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views.generic.base import TemplateView
from notifications import models as notifications_models
from notifications import notify
from urbanvitaliz.apps.addressbook.models import Organization
from urbanvitaliz.apps.projects.models import Project, UserProjectStatus
from urbanvitaliz.apps.resources.models import Resource
from urbanvitaliz.utils import check_if_switchtender, get_site_administrators
from watson import search as watson

from . import forms, models


class CRMSiteDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "crm/site_dashboard.html"

    def test_func(self):
        return check_if_switchtender(self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["search_form"] = forms.CRMSearchForm()
        context["projects_waiting"] = Project.on_site.filter(status="DRAFT").count()
        context["project_model"] = Project
        context["user_model"] = User

        ctype = ContentType.objects.get_for_model(Project)
        context["projects_stream"] = Action.objects.filter(
            Q(target_content_type=ctype)
            | Q(action_object_content_type=ctype)
            | Q(actor_content_type=ctype)
        )

        return context


@staff_member_required
def crm_search(request):
    if request.method == "POST":
        search_form = forms.CRMSearchForm(request.POST)

        if search_form.is_valid():
            query = search_form.cleaned_data["query"]
            search_results = watson.search(query, exclude=(Resource,))

    else:
        search_form = forms.CRMSearchForm()

    return render(request, "crm/search_results.html", locals())


@staff_member_required
def organization_details(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)

    participants = User.objects.filter(
        profile__in=organization.registered_profiles.all()
    )

    advised_projects = Project.on_site.filter(switchtenders__in=participants)

    org_departments = organization.departments.all()

    unadvised_projects = Project.on_site.filter(
        commune__department__in=org_departments
    ).exclude(switchtenders__in=participants)

    participant_ids = list(participants.values_list("id", flat=True))

    user_ct = ContentType.objects.get_for_model(User)

    actions = Action.objects.filter(
        site=request.site,
        actor_content_type=user_ct,
        actor_object_id__in=participant_ids,
    )

    organization_ct = ContentType.objects.get_for_model(Organization)

    unread_notifications = (
        notifications_models.Notification.on_site.unread()
        .filter(recipient=request.user, public=False)
        .filter(target_content_type=organization_ct, target_object_id=organization.pk)
    )

    org_notes = models.Note.on_site.filter(
        object_id=organization.pk,
        content_type=organization_ct,
    ).order_by("-updated_on")

    participant_notes = models.Note.on_site.filter(
        object_id__in=participant_ids,
        content_type=user_ct,
    ).order_by("-updated_on")

    sticky_notes = org_notes.filter(sticky=True)
    notes = org_notes.exclude(sticky=True) | participant_notes

    search_form = forms.CRMSearchForm()

    return render(request, "crm/organization_details.html", locals())


@staff_member_required
def user_details(request, user_id):
    crm_user = get_object_or_404(User, pk=user_id)

    actions = actor_stream(crm_user)

    user_ct = ContentType.objects.get_for_model(User)

    # Burn notification for this viewed user
    notifications_models.Notification.on_site.unread().filter(
        recipient=request.user, public=False
    ).filter(
        action_object_content_type=user_ct, action_object_object_id=crm_user.pk
    ).mark_all_as_read()

    all_notes = models.Note.on_site.filter(
        object_id=crm_user.pk, content_type=user_ct
    ).order_by("-updated_on")
    sticky_notes = all_notes.filter(sticky=True)
    notes = all_notes.exclude(sticky=True)

    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_details.html", locals())


@staff_member_required
def user_project_interest(request, user_id):
    crm_user = get_object_or_404(User, pk=user_id)

    actions = actor_stream(crm_user)

    user_ct = ContentType.objects.get_for_model(User)

    statuses = UserProjectStatus.objects.filter(user=crm_user).order_by("project__name")

    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_project_interest.html", locals())


@staff_member_required
def user_notifications(request, user_id):
    crm_user = get_object_or_404(User, pk=user_id)

    search_form = forms.CRMSearchForm()

    notifications = notifications_models.Notification.on_site.filter(
        recipient=crm_user, emailed=True
    )[:100]

    return render(request, "crm/user_notifications.html", locals())


@staff_member_required
def project_details(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    actions = target_stream(project)

    project_ct = ContentType.objects.get_for_model(Project)

    all_notes = models.Note.on_site.filter(
        object_id=project.pk, content_type=project_ct
    ).order_by("-updated_on")
    sticky_notes = all_notes.filter(sticky=True)
    notes = all_notes.exclude(sticky=True)

    search_form = forms.CRMSearchForm()

    return render(request, "crm/project_details.html", locals())


def handle_create_note_for_object(
    request, the_object, return_view_name, return_update_view_name
):
    if request.method == "POST":
        form = forms.CRMNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.related = the_object
            note.created_by = request.user
            note.site = request.site
            note.save()
            return True, redirect(reverse(return_view_name, args=(the_object.pk,)))

    else:
        form = forms.CRMNoteForm()

    return False, render(request, "crm/note_create.html", locals())


@staff_member_required
def create_note_for_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    created, response = handle_create_note_for_object(
        request, user, "crm-user-details", "crm-user-note-update"
    )

    if created and user.profile and user.profile.organization:
        administrators = get_site_administrators(request.site).exclude(
            pk=request.user.pk
        )  # XXX Should be replaced by crm users once new permissions are merged
        notify.send(
            sender=request.user,
            recipient=administrators,
            verb="a créé une note de CRM",
            action_object=user,
            target=user.profile.organization,
            public=False,
            crm=True,
        )

    return response


@staff_member_required
def create_note_for_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    _, response = handle_create_note_for_object(
        request, project, "crm-project-details", "crm-project-note-update"
    )

    return response


@staff_member_required
def create_note_for_organization(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)

    _, response = handle_create_note_for_object(
        request,
        organization,
        "crm-organization-details",
        "crm-organization-note-update",
    )

    return response


def update_note_for_object(request, note, return_view_name):
    if request.method == "POST":
        form = forms.CRMNoteForm(request.POST, instance=note)
        if form.is_valid():
            note = form.save(commit=False)
            note.updated_on = timezone.now()
            note.save()
            form.save_m2m()
            return redirect(reverse(return_view_name, args=(note.related.pk,)))
    else:
        form = forms.CRMNoteForm(instance=note)

    return render(request, "crm/note_update.html", locals())


@staff_member_required
def update_note_for_user(request, user_id, note_id):
    user = get_object_or_404(User, pk=user_id)
    user_ct = ContentType.objects.get_for_model(user)
    note = get_object_or_404(
        models.Note,
        site=request.site,
        object_id=user_id,
        content_type=user_ct,
        pk=note_id,
    )

    return update_note_for_object(request, note, "crm-user-details")


@staff_member_required
def update_note_for_project(request, project_id, note_id):
    project = get_object_or_404(Project, pk=project_id)
    project_ct = ContentType.objects.get_for_model(project)
    note = get_object_or_404(
        models.Note,
        site=request.site,
        object_id=project_id,
        content_type=project_ct,
        pk=note_id,
    )

    return update_note_for_object(request, note, "crm-project-details")


@staff_member_required
def update_note_for_organization(request, organization_id, note_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    organization_ct = ContentType.objects.get_for_model(organization)
    note = get_object_or_404(
        models.Note,
        site=request.site,
        object_id=organization_id,
        content_type=organization_ct,
        pk=note_id,
    )

    return update_note_for_object(request, note, "crm-organization-details")


########################################################################
# RSS Feeds
########################################################################


class LatestNotesFeed(Feed):
    title = "Dernières notes de CRM"
    link = "/crm/feed"
    description = "Dernières notes"

    def items(self):
        return models.Note.on_site.order_by("-updated_on", "-created_on")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.created_on

    def item_updateddate(self, item):
        return item.updated_on


# eof
