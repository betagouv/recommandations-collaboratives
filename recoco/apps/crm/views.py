"""
Views for crm application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-07-20 12:27:25 CEST
"""

import csv
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime, timedelta

from actstream import action
from actstream.models import Action, actor_stream, target_stream
from allauth.account.models import EmailAddress
from allauth.account.utils import (
    filter_users_by_email,
    send_email_confirmation,
    setup_user_email,
)
from django import forms as django_forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.db import transaction
from django.db.models import Count, ExpressionWrapper, F, FloatField, Max, Q, Value
from django.db.models.functions import Cast
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_http_methods
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from guardian.shortcuts import get_users_with_perms
from notifications import models as notifications_models
from notifications import notify
from watson import search as watson

from recoco import verbs
from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.addressbook.models import Organization
from recoco.apps.communication import api
from recoco.apps.geomatics import models as geomatics
from recoco.apps.home import models as home_models
from recoco.apps.onboarding import utils as onboarding_utils
from recoco.apps.projects.models import Project, Topic
from recoco.apps.reminders import models as reminders_models
from recoco.apps.tasks.models import Task
from recoco.utils import (
    get_group_for_site,
    get_site_config_or_503,
    has_perm,
    has_perm_or_403,
    make_group_name_for_site,
)

from . import filters, forms, models
from .forms import SiteConfigurationForm


class CRMSiteDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "crm/site_dashboard.html"

    def test_func(self):
        return has_perm(self.request.user, "use_crm", self.request.site)

    def get_context_data(self, *orgs, **kwargs):
        context = super().get_context_data(*orgs, **kwargs)
        context["search_form"] = forms.CRMSearchForm()
        context["projects_waiting"] = Project.on_site.filter(
            project_sites__status="DRAFT", project_sites__site=self.request.site
        ).count()
        context["project_model"] = Project
        context["user_model"] = User

        ctype = ContentType.objects.get_for_model(Project)
        context["projects_stream"] = (
            Action.objects.filter(site=self.request.site)
            .filter(
                Q(target_content_type=ctype)
                | Q(action_object_content_type=ctype)
                | Q(actor_content_type=ctype)
            )
            .order_by("-timestamp")
            .prefetch_related("actor", "action_object", "target")[:100]
        )

        context["crm_notif_stream"] = (
            self.request.user.notifications.filter(public=False)
            .filter(site=self.request.site)
            .filter(Q(verb=verbs.CRM.NOTE_CREATED))
            .order_by("-timestamp")
            .prefetch_related("actor", "action_object", "target")
        )

        # Consume notifications
        if not self.request.user.is_hijacked:
            context["crm_notif_stream"].mark_all_as_read()

        return context


@login_required
def crm_search(request):
    has_perm_or_403(request.user, "use_crm", request.site)

    search_form = forms.CRMSearchForm(request.POST or request.GET or None)

    if search_form.is_valid():
        site = request.site
        query = search_form.cleaned_data["query"]

        all_sites_search_results = watson.search(
            query,
            models=(
                Project,
                models.ProjectAnnotations,
                User,
                Organization,
                models.Note,
            ),
        )

        def filter_current_site(entry):
            """Since watson does not support related model field filtering,
            take care of that afterwards"""
            obj = entry.object

            if hasattr(obj, "sites"):
                if request.site in obj.sites.all():
                    return True

            if hasattr(obj, "site"):
                if request.site == obj.site:
                    return True

            if hasattr(obj, "profile"):
                if request.site in obj.profile.sites.all():
                    return True

            return False

        search_results = list(filter(filter_current_site, all_sites_search_results))

    return render(request, "crm/search_results.html", locals())


########################################################################
# tenancy
########################################################################


class SiteConfigurationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = SiteConfigurationForm
    template_name = "crm/siteconfiguration_update.html"
    success_url = reverse_lazy("crm-site-dashboard")

    def test_func(self):
        return has_perm(
            self.request.user, "sites.manage_configuration", self.request.site
        )

    def get_object(self, queryset=None):
        return self.request.site.configuration


########################################################################
# organizations
########################################################################


def get_queryset_for_site_organizations(site):
    """Return queryset of organizations from addressbook site or w/ user on site"""
    return Organization.objects.filter(
        Q(sites=site) | Q(registered_profiles__sites=site)
    ).distinct()


@login_required
def organization_list(request):
    has_perm_or_403(request.user, "use_crm", request.site)

    # organization from addressbook current site or w/ user on site
    qs = get_queryset_for_site_organizations(request.site)

    organizations = filters.OrganizationFilter(
        request.GET,
        queryset=qs.order_by("name"),
    )

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/organization_list.html", locals())


@login_required
def organization_update(request, organization_id=None):
    has_perm_or_403(request.user, "use_crm", request.site)

    qs = get_queryset_for_site_organizations(request.site)
    organization = get_object_or_404(qs, pk=organization_id)

    if request.method == "POST":
        form = forms.CRMOrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            return redirect(reverse("crm-organization-details", args=[organization.id]))
    else:
        form = forms.CRMOrganizationForm(instance=organization)

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/organization_update.html", locals())


@login_required
def organization_merge(request):
    has_perm_or_403(request.user, "use_crm", request.site)

    qs = get_queryset_for_site_organizations(request.site)

    if request.method == "POST":
        name = request.POST.get("name")
        ids = request.POST.getlist("org_ids", [])
        if not ids:
            return redirect(reverse("crm-organization-list"))
        orgs = [get_object_or_404(qs, pk=id) for id in ids]
        # process to merging of data
        with transaction.atomic():
            update_contacts(orgs)
            update_profiles(orgs)
            merge_organizations_with_name(orgs, name)
        return redirect(reverse("crm-organization-list"))

    merge_form = forms.CRMOrganizationMergeForm(request.GET)

    # required by default on crm
    search_form = forms.CRMSearchForm()

    # get organizations and dependencies for merge summary
    ids = request.GET.getlist("org_ids", [])
    if not ids:
        return redirect(reverse("crm-organization-list"))
    organizations = [get_object_or_404(qs, pk=id) for id in ids]
    departments = geomatics.Department.objects.filter(organizations__in=organizations)
    profiles = home_models.UserProfile.objects.filter(organization__in=organizations)
    contacts = addressbook_models.Contact.objects.filter(organization__in=organizations)

    # first request confirmation for merging
    return render(request, "crm/organization_merge.html", locals())


def update_contacts(orgs):
    """Update all the contacts referencing the old organization to the new one"""
    new_org = orgs[0]
    contacts = addressbook_models.Contact.objects.filter(organization__in=orgs)
    contacts.update(organization=new_org)


def update_profiles(orgs):
    """Update all the profiles referencing the old organization to the new one"""
    new_org = orgs[0]
    profiles = home_models.UserProfile.objects.filter(organization__in=orgs)
    profiles.update(organization=new_org)


def merge_organizations_with_name(orgs, name):
    """Merge all orgs departments into first one, and rename it, del all others"""
    new_org = orgs[0]
    old_orgs = orgs[1:]
    # update old depts in new organization
    departments = [
        d for d in geomatics.Department.objects.filter(organizations__in=old_orgs)
    ]
    new_org.departments.add(*departments)
    # update old sites in new organization
    sites = [s for s in Site.objects.filter(organizations__in=old_orgs)]
    new_org.sites.add(*sites)
    # update new organization name
    new_org.name = name
    new_org.save()
    # delete old orgs
    old_ids = [o.id for o in old_orgs]
    addressbook_models.Organization.objects.filter(id__in=old_ids).delete()


@login_required
def organization_details(request, organization_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    qs = get_queryset_for_site_organizations(request.site)
    organization = get_object_or_404(qs, pk=organization_id)

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

    actions = (
        Action.objects.filter(site=request.site)
        .filter(
            actor_content_type=user_ct,
            actor_object_id__in=participant_ids,
        )
        .order_by("-timestamp")
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


########################################################################
# users
########################################################################


@login_required
def user_list(request):
    has_perm_or_403(request.user, "use_crm", request.site)

    # filtered users
    users = filters.UserFilter(
        request.GET,
        queryset=User.objects.filter(profile__sites=request.site).prefetch_related(
            "profile__organization"
        ),
    )

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_list.html", locals())


@login_required
def user_update(request, user_id=None):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id, profile__sites=request.site)
    profile = crm_user.profile

    group_name = make_group_name_for_site("advisor", request.site)
    crm_user_is_advisor = crm_user.groups.filter(name=group_name).exists()

    if request.method == "POST":
        form = forms.CRMProfileForm(request.POST, instance=profile)
        if form.is_valid():
            with transaction.atomic():
                username = form.cleaned_data.get("username")
                email_changed = username != crm_user.username
                if email_changed:
                    users = filter_users_by_email(username)
                    if len(users) > 0:
                        # a user with the new mail already exist
                        if request.site in users[0].profile.sites.all():  # on same site
                            user_link = reverse("crm-user-details", args=[users[0].pk])
                            error_msg = mark_safe(  # noqa: S308
                                f'L\'utilisateur <a href="{user_link}">'
                                f"{users[0].first_name} {users[0].last_name}</a>'"
                                " utilise déjà cette adresse email."
                            )  # nosec
                            form.add_error(
                                "username", django_forms.ValidationError(error_msg)
                            )
                        else:  # on an other site
                            form.add_error(
                                "username",
                                django_forms.ValidationError(
                                    "L'adresse email est déjà utilisée."
                                ),
                            )

                    else:
                        # delete old email address
                        EmailAddress.objects.filter(user=crm_user).delete()

                        # setup new email address
                        crm_user.username = username
                        crm_user.email = username

                if form.is_valid():  # maybe email update threw an error in the meantime
                    # update profile object
                    form.save()

                    # update user object
                    crm_user.first_name = form.cleaned_data.get("first_name")
                    crm_user.last_name = form.cleaned_data.get("last_name")
                    crm_user.save()

                    success_message = (
                        "Les informations de l'utilisateur ont "
                        "été modifiées avec succès."
                    )
                    if email_changed:
                        setup_user_email(request, crm_user, [])
                        send_email_confirmation(request, crm_user, signup=True)

                    messages.success(request, success_message)
                    return redirect(reverse("crm-user-details", args=[crm_user.id]))
    else:
        form = forms.CRMProfileForm(
            instance=profile,
            initial={
                "username": crm_user.username,
                "first_name": crm_user.first_name,
                "last_name": crm_user.last_name,
            },
        )

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_update.html", locals())


@login_required
def user_deactivate(request, user_id=None):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id, profile__sites=request.site)

    if request.method == "POST":
        crm_user.is_active = False
        crm_user.save()
        profile = crm_user.profile
        profile.deleted = timezone.now()
        profile.save()
        return redirect(reverse("crm-user-details", args=[crm_user.id]))

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_deactivate.html", locals())


@login_required
def user_reactivate(request, user_id=None):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id, profile__sites=request.site)

    if request.method == "POST":
        crm_user.is_active = True
        crm_user.save()
        profile = crm_user.profile
        profile.deleted = None
        profile.save()
        return redirect(reverse("crm-user-details", args=[crm_user.id]))

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_reactivate.html", locals())


@login_required
def user_set_advisor(request, user_id=None):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id, profile__sites=request.site)
    profile = crm_user.profile

    if request.method == "POST":
        form = forms.CRMAdvisorForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            group = get_group_for_site("advisor", request.site)
            crm_user.groups.add(group)
            return redirect(reverse("crm-user-details", args=[crm_user.id]))
    else:
        form = forms.CRMAdvisorForm(instance=profile)

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_set_advisor.html", locals())


@login_required
def user_unset_advisor(request, user_id=None):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id, profile__sites=request.site)
    profile = crm_user.profile

    if request.method == "POST":
        profile.departments.clear()
        group = get_group_for_site("advisor", request.site)
        crm_user.groups.remove(group)
        return redirect(reverse("crm-user-details", args=[crm_user.id]))

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_unset_advisor.html", locals())


@login_required
def user_details(request, user_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id, profile__sites=request.site)

    group_name = make_group_name_for_site("advisor", request.site)
    crm_user_is_advisor = crm_user.groups.filter(name=group_name).exists()

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


@login_required
def user_notifications(request, user_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id, profile__sites=request.site)

    if request.site not in crm_user.profile.sites.all():
        # only for user of current site
        raise Http404

    search_form = forms.CRMSearchForm()

    notifications = notifications_models.Notification.on_site.filter(
        recipient=crm_user, emailed=True
    )[:100]

    return render(request, "crm/user_notifications.html", locals())


@login_required
def user_reminders(request, user_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id, profile__sites=request.site)

    if request.site not in crm_user.profile.sites.all():
        # only for user of current site
        raise Http404

    search_form = forms.CRMSearchForm()

    sent_reminders = reminders_models.Reminder.on_site.filter(
        sent_to=crm_user
    ).order_by("-deadline")[:100]

    future_reminders = reminders_models.Reminder.on_site.filter(
        project__in=Project.on_site.filter(
            projectmember__member=crm_user, projectmember__is_owner=True
        ),
        sent_on=None,
    ).order_by("-deadline")

    return render(request, "crm/user_reminders.html", locals())


@login_required
def user_reminder_details(request, user_id, reminder_pk):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id, profile__sites=request.site)
    if request.site not in crm_user.profile.sites.all():
        # only for user of current site
        raise Http404

    reminder = get_object_or_404(
        reminders_models.Reminder, pk=reminder_pk, site=request.site, sent_to=crm_user
    )

    email = None
    if reminder.transactions.count():
        transaction = reminder.transactions.first()
        if transaction:
            email = api.fetch_transaction_content(transaction.transaction_id)

    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_reminder_details.html", locals())


########################################################################
# projects
########################################################################


@login_required
def project_list(request):
    has_perm_or_403(request.user, "use_crm", request.site)

    # filtered projects
    projects = filters.ProjectFilter(
        request.GET,
        queryset=Project.all_on_site.order_by("name").prefetch_related("commune"),
    )

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/project_list.html", locals())


@login_required
def project_details(request, project_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    project = get_object_or_404(Project.all_on_site, pk=project_id)

    site_config = get_site_config_or_503(request.site)

    site_origin = project.project_sites.get(is_origin=True)

    actions = target_stream(project)

    user_ct = ContentType.objects.get_for_model(User)

    project_ct = ContentType.objects.get_for_model(Project)

    participants = project.members.all()
    participant_ids = list(participants.values_list("id", flat=True))
    participant_notes = models.Note.on_site.filter(
        object_id__in=participant_ids,
        content_type=user_ct,
    ).order_by("-updated_on")

    project_notes = models.Note.on_site.filter(
        object_id=project.pk, content_type=project_ct
    ).order_by("-updated_on")

    sticky_notes = project_notes.filter(sticky=True)

    notes = project_notes.exclude(sticky=True) | participant_notes

    search_form = forms.CRMSearchForm()

    return render(request, "crm/project_details.html", locals())


@login_required
def project_update(request, project_id=None):
    """Update project properties"""
    has_perm_or_403(request.user, "use_crm", request.site)
    project = get_object_or_404(Project.on_site, pk=project_id)

    if request.method == "POST":
        form = forms.CRMProjectForm(request.POST)
        if form.is_valid():
            if "notifications" in form.cleaned_data:
                project.muted = not form.cleaned_data["notifications"]
            if "statistics" in form.cleaned_data:
                project.exclude_stats = not form.cleaned_data["statistics"]
            project.save()
    else:
        form = forms.CRMProjectForm(
            initial={
                "statistics": not project.exclude_stats,
                "notifications": not project.muted,
            }
        )

    search_form = forms.CRMSearchForm()

    return render(request, "crm/project_update.html", locals())


@login_required
def project_delete(request, project_id=None):
    """Delete project"""
    has_perm_or_403(request.user, "use_crm", request.site)
    project = get_object_or_404(Project.on_site, pk=project_id)
    if request.method == "POST":
        project.deleted = timezone.now()
        project.save()
        return redirect("crm-project-list")
    return render(request, "crm/project_delete.html", locals())


@login_required
def project_undelete(request, project_id=None):
    """Undelete project"""
    has_perm_or_403(request.user, "use_crm", request.site)
    project = get_object_or_404(Project.deleted_on_site, pk=project_id)
    if request.method == "POST":
        project.deleted = None
        project.save()
        return redirect("crm-project-list")
    return render(request, "crm/project_undelete.html", locals())


@login_required
@require_http_methods(["POST"])
def project_toggle_annotation(request, project_id=None):
    has_perm_or_403(request.user, "use_crm", request.site)

    project = get_object_or_404(Project.on_site, pk=project_id)

    site_config = get_site_config_or_503(request.site)

    form = forms.ProjectAnnotationForm(request.POST)
    if form.is_valid():
        tag = form.cleaned_data.get("tag")
        # check if the tag is authorized by the site configuration
        if tag in site_config.crm_available_tags.values_list("name", flat=True):
            annotation, _ = models.ProjectAnnotations.objects.get_or_create(
                project=project, site=request.site
            )
            if tag in annotation.tags.names():
                annotation.tags.remove(tag)
            else:
                annotation.tags.add(tag)

    url = reverse("crm-project-details", args=[project.id])
    return redirect(url)


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
            form.save_m2m()
            return note, redirect(reverse(return_view_name, args=(the_object.pk,)))
    else:
        form = forms.CRMNoteForm()

    return None, render(request, "crm/note_create.html", locals())


@login_required
def create_note_for_user(request, user_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    user = get_object_or_404(User, pk=user_id)
    if request.site not in user.profile.sites.all():
        raise Http404()

    note, response = handle_create_note_for_object(
        request, user, "crm-user-details", "crm-user-note-update"
    )

    # FIXME check that user.profile has any meaning or remove
    # FIXME if user.profile has no meaning move notification into handle
    if note and user.profile:
        notify_note_creation(request, note, user)

    return response


@login_required
def create_note_for_project(request, project_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    project = get_object_or_404(Project.on_site, pk=project_id)

    note, response = handle_create_note_for_object(
        request, project, "crm-project-details", "crm-project-note-update"
    )

    if note:
        notify_note_creation(request, note, project)

    return response


@login_required
def create_note_for_organization(request, organization_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    qs = get_queryset_for_site_organizations(request.site)
    organization = get_object_or_404(qs, pk=organization_id)

    note, response = handle_create_note_for_object(
        request,
        organization,
        "crm-organization-details",
        "crm-organization-note-update",
    )

    if note:
        notify_note_creation(request, note, organization)

    return response


def notify_note_creation(request, note, target):
    """Notify crm users of new note creation"""
    # TODO only create action stream not emails
    action.send(
        request.user,
        verb=verbs.CRM.NOTE_CREATED,
        action_object=note,
        target=target,
    )
    return
    crm_users = get_users_with_perms(
        request.site, only_with_perms_in=["use_crm"]
    ).exclude(pk=request.user.pk)

    notify.send(
        sender=request.user,
        recipient=crm_users,
        verb=verbs.CRM.NOTE_CREATED,
        action_object=note,
        target=target,
        public=False,
    )


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


@login_required
def update_note_for_user(request, user_id, note_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    user = get_object_or_404(User, pk=user_id)
    if request.site not in user.profile.sites.all():
        raise Http404()

    user_ct = ContentType.objects.get_for_model(user)
    note = get_object_or_404(
        models.Note.on_site,
        site=request.site,
        object_id=user_id,
        content_type=user_ct,
        pk=note_id,
    )

    return update_note_for_object(request, note, "crm-user-details")


@login_required
def update_note_for_project(request, project_id, note_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    project = get_object_or_404(Project.on_site, pk=project_id)
    project_ct = ContentType.objects.get_for_model(project)
    note = get_object_or_404(
        models.Note.on_site,
        site=request.site,
        object_id=project_id,
        content_type=project_ct,
        pk=note_id,
    )

    return update_note_for_object(request, note, "crm-project-details")


@login_required
def update_note_for_organization(request, organization_id, note_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    qs = get_queryset_for_site_organizations(request.site)
    organization = get_object_or_404(qs, pk=organization_id)

    organization_ct = ContentType.objects.get_for_model(organization)
    note = get_object_or_404(
        models.Note.on_site,
        site=request.site,
        object_id=organization_id,
        content_type=organization_ct,
        pk=note_id,
    )

    return update_note_for_object(request, note, "crm-organization-details")


@login_required
def crm_list_recommendation_without_resources(request):
    """Return a page containing all recommendations with no resource attached"""
    has_perm_or_403(request.user, "use_crm", request.site)

    search_form = forms.CRMSearchForm()

    recommendations = (
        Task.on_site.filter(public=True, resource=None)
        .exclude(project__exclude_stats=True)
        .order_by("-created_on", "project")
    )

    return render(request, "crm/reco_without_resources.html", locals())


@login_required
def crm_list_projects_with_low_reach(request):
    """List projects that don't get a good impact"""
    has_perm_or_403(request.user, "use_crm", request.site)

    site_config = get_site_config_or_503(request.site)

    search_form = forms.CRMSearchForm()

    low_reach_projects = (
        Project.on_site.filter(
            project_sites__status__in=("READY", "IN_PROGRESS", "DONE"),
            project_sites__site=request.site,
        )
        .exclude(exclude_stats=True)
        .prefetch_related("tasks", "notes", "switchtenders")
        .annotate(
            reco_total=Count(
                "tasks",
                filter=Q(tasks__public=True, tasks__deleted=None),
                distinct=True,
            ),
            reco_read=Count(
                "tasks",
                filter=Q(tasks__public=True, tasks__visited=True, tasks__deleted=None),
                distinct=True,
            ),
        )
        .exclude(reco_total=0)
        .annotate(
            reco_read_ratio=ExpressionWrapper(
                Cast(F("reco_read"), FloatField()) / F("reco_total") * Value(100.0),
                output_field=FloatField(),
            ),  # Pc of unread reco
            last_reco_at=Max("tasks__created_on", filter=Q(tasks__public=True)),
            last_public_msg_at=Max(
                "notes__created_on",
                filter=Q(notes__public=True, notes__created_by__in=F("members__id")),
            ),
        )
        .exclude(reco_read_ratio__gte=99.9)  # Not interested if everything was read
        .exclude(
            last_reco_at__lte=datetime.now()
            - timedelta(days=site_config.reminder_interval)
        )
        .order_by(
            "reco_read_ratio",
            "last_members_activity_at",
            "last_reco_at",
            "last_public_msg_at",
        )
        .distinct()
    )

    return render(request, "crm/projects_low_reach.html", locals())


@login_required
def crm_list_tags(request):
    """Return a page containing all tags with their count"""
    has_perm_or_403(request.user, "use_crm", request.site)

    search_form = forms.CRMSearchForm()

    tags = compute_tag_occurences(request.site)
    return render(request, "crm/tagcloud.html", locals())


def compute_tag_occurences(site):
    project_tags = dict(
        (tag["name"], tag["occurrences"])
        for tag in (
            models.ProjectAnnotations.tags.filter(projectannotations__site=site)
            .distinct()
            .values("name")
            .annotate(occurrences=Count("projectannotations", distinct=True))
        )
    )

    note_tags = dict(
        (tag["name"], tag["occurrences"])
        for tag in (
            models.Note.tags.filter(note__site=site)
            .distinct()
            .values("name")
            .annotate(occurrences=Count("note", distinct=True))
        )
    )

    tags = Counter(**project_tags) + Counter(**note_tags)
    return OrderedDict(sorted(tags.items()))


def compute_topics_occurences(site):
    project_topics = defaultdict(
        list,
        (
            (topic.name, list(topic.projects.all()))
            for topic in (
                Topic.objects.filter(projects__sites=site, projects__deleted=None)
                .prefetch_related("projects")
                .distinct()
            )
        ),
    )

    task_topics = defaultdict(
        list,
        (
            (topic.name, list(topic.tasks.all()))
            for topic in (
                Topic.objects.filter(tasks__site=site, tasks__deleted=None)
                .prefetch_related("tasks")
                .prefetch_related("tasks__project")
                .distinct()
            )
        ),
    )

    topics = {}
    for key in project_topics.keys() | task_topics.keys():
        topics[key] = (
            len(project_topics[key]) + len(task_topics[key]),
            project_topics[key],
            task_topics[key],
        )

    return OrderedDict(sorted(topics.items()))


@login_required
def crm_list_topics(request):
    """Return a page containing all topics with their count and attached objects"""
    has_perm_or_403(request.user, "use_crm", request.site)

    search_form = forms.CRMSearchForm()

    topics = compute_topics_occurences(request.site)
    topics_wc = OrderedDict(sorted((key, value[0]) for key, value in topics.items()))

    return render(request, "crm/topics.html", locals())


@login_required
def crm_list_topics_as_csv(request):
    """Return a CSV containing all topics with their count and attached objects"""
    has_perm_or_403(request.user, "use_crm", request.site)

    topics = compute_topics_occurences(request.site)

    today = datetime.today().date()

    content_disposition = (
        f'attachment; filename="topics-for-projects-and-recos-{today}.csv"'
    )
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": content_disposition,
        },
    )

    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    writer.writerow(
        [
            "topic",
            "usage_count",
            "project_ids",
            "reco_ids",
        ]
    )

    for name, usage in topics.items():
        writer.writerow(
            [
                name,
                usage[0],
                [project.pk for project in usage[1]],
                [task.pk for task in usage[2]],
            ]
        )

    return response


@login_required
def project_list_by_tags(request):
    """Return a page containing for each tag the projects using it"""
    has_perm_or_403(request.user, "use_crm", request.site)

    tags = (
        Project.tags.filter(project__sites=request.site)
        .exclude(project__exclude_stats=True)
        .annotate(Count("project", distinct=True))
        .order_by("-project__count")
        .distinct()
    )

    search_form = forms.CRMSearchForm()

    return render(request, "crm/tags_for_projects.html", locals())


@login_required
def project_list_by_tags_as_csv(request):
    has_perm_or_403(request.user, "use_crm", request.site)

    tags = (
        Project.tags.filter(project__sites=request.site)
        .exclude(project__exclude_stats=True)
        .annotate(Count("project", distinct=True))
        .order_by("-project__count")
        .distinct()
    )

    today = datetime.today().date()

    content_disposition = f'attachment; filename="tags-for-projects-{today}.csv"'
    response = HttpResponse(
        content_type="text/csv",
        headers={
            "Content-Disposition": content_disposition,
        },
    )

    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    writer.writerow(
        [
            "tag",
            "usage_count",
            "project_ids",
            "project_names",
        ]
    )

    for tag in tags:
        projects = Project.on_site.filter(tags__name=tag.name).order_by("name")
        writer.writerow(
            [
                tag.name,
                tag.project__count,
                list(projects.values_list(flat=True)),
                ", ".join([f'"{p.name}"' for p in projects]),
            ]
        )

    return response


@login_required
def projects_activity_feed(request):
    has_perm_or_403(request.user, "use_crm", request.site)

    ctype = ContentType.objects.get_for_model(Project)

    actions = (
        Action.objects.filter(site=request.site)
        .filter(
            Q(target_content_type=ctype)
            | Q(action_object_content_type=ctype)
            | Q(actor_content_type=ctype)
        )
        .order_by("-timestamp")
        .prefetch_related("actor", "action_object", "target")[:500]
    )

    search_form = forms.CRMSearchForm()

    return render(request, "crm/projects_activity_feed.html", locals())


################
# Project Handover to another Site
################


@login_required
def project_site_handover(request, project_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    project = get_object_or_404(
        Project,
        Q(project_sites__site=request.site) & ~Q(project_sites__status="DRAFT"),
        pk=project_id,
    )

    available_sites = (
        (Site.objects.filter(configuration__accept_handover=True) | project.sites.all())
        .distinct()
        .order_by("name")
    )

    if request.method == "POST":
        form = forms.ProjectHandover(request.POST)
        if form.is_valid():
            site = form.cleaned_data["site"]

            project.project_sites.create(
                site=site,
                sent_by=request.user,
                sent_from=request.site,
                is_origin=False,
                status="DRAFT",
            )
            onboarding_utils.notify_new_project(
                site=site, project=project, owner=project.owner
            )

            messages.add_message(
                request,
                messages.SUCCESS,
                f"Le projet {project.name} a bien été proposé au portail '{site.name}'",
            )

            return redirect(reverse("crm-project-handover", args=(project.pk,)))

    return render(request, "crm/project_site_handover.html", locals())


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
        result = ""

        if item.kind:
            result = f"#{item.get_kind_display()} // "

        if item.title:
            result = f"{result}{item.title} - "

        return f"{result}{item.related}"

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.created_on

    def item_updateddate(self, item):
        return item.updated_on


# eof
