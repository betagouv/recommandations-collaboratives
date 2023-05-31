"""
Views for crm application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-07-20 12:27:25 CEST
"""

import csv
import datetime
from collections import Counter, OrderedDict

from actstream.models import Action, actor_stream, target_stream
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.views import Feed
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic.base import TemplateView
from guardian.shortcuts import get_users_with_perms
from notifications import models as notifications_models
from notifications import notify
from urbanvitaliz.apps.addressbook.models import Organization
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.home import models as home_models
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects.models import Project, UserProjectStatus
from urbanvitaliz.utils import (
    get_group_for_site,
    has_perm,
    has_perm_or_403,
    make_group_name_for_site,
)
from watson import search as watson

from . import filters, forms, models


class CRMSiteDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "crm/site_dashboard.html"

    def test_func(self):
        return has_perm(self.request.user, "use_crm", self.request.site)

    def get_context_data(self, *orgs, **kwargs):
        context = super().get_context_data(*orgs, **kwargs)
        context["search_form"] = forms.CRMSearchForm()
        context["projects_waiting"] = Project.on_site.filter(status="DRAFT").count()
        context["project_model"] = Project
        context["user_model"] = User

        ctype = ContentType.objects.get_for_model(Project)
        context["projects_stream"] = Action.objects.filter(
            Q(target_content_type=ctype)
            | Q(action_object_content_type=ctype)
            | Q(actor_content_type=ctype)
        ).prefetch_related("actor", "action_object", "target")

        return context


@login_required
def crm_search(request):
    has_perm_or_403(request.user, "use_crm", request.site)

    search_form = forms.CRMSearchForm(request.POST or request.GET or None)

    if search_form.is_valid():
        site = request.site
        query = search_form.cleaned_data["query"]
        project_results = watson.filter(
            Project.objects.filter(sites=request.site), query, ranking=True
        )

        search_results = list(project_results)

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

    crm_user = get_object_or_404(User, pk=user_id)
    profile = crm_user.profile

    group_name = make_group_name_for_site("advisor", request.site)
    crm_user_is_advisor = crm_user.groups.filter(name=group_name).exists()

    if request.method == "POST":
        form = forms.CRMProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # update profile object
            form.save()
            # update user object
            crm_user.first_name = form.cleaned_data.get("first_name")
            crm_user.last_name = form.cleaned_data.get("last_name")
            crm_user.save()
            return redirect(reverse("crm-user-details", args=[crm_user.id]))
    else:
        form = forms.CRMProfileForm(
            instance=profile,
            initial={
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

    crm_user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        crm_user.is_active = False
        crm_user.save()
        return redirect(reverse("crm-user-details", args=[crm_user.id]))

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_deactivate.html", locals())


@login_required
def user_reactivate(request, user_id=None):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        crm_user.is_active = True
        crm_user.save()
        return redirect(reverse("crm-user-details", args=[crm_user.id]))

    # required by default on crm
    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_reactivate.html", locals())


@login_required
def user_set_advisor(request, user_id=None):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id)
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

    crm_user = get_object_or_404(User, pk=user_id)
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

    crm_user = get_object_or_404(User, pk=user_id)

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
def user_project_interest(request, user_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id)

    if request.site not in crm_user.profile.sites.all():
        # only for user of current site
        raise Http404

    actions = actor_stream(crm_user)

    user_ct = ContentType.objects.get_for_model(User)

    statuses = UserProjectStatus.objects.filter(user=crm_user).order_by("project__name")

    search_form = forms.CRMSearchForm()

    return render(request, "crm/user_project_interest.html", locals())


@login_required
def user_notifications(request, user_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    crm_user = get_object_or_404(User, pk=user_id)

    if request.site not in crm_user.profile.sites.all():
        # only for user of current site
        raise Http404

    search_form = forms.CRMSearchForm()

    notifications = notifications_models.Notification.on_site.filter(
        recipient=crm_user, emailed=True
    )[:100]

    return render(request, "crm/user_notifications.html", locals())


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

    form = forms.ProjectAnnotationForm(request.POST)
    if form.is_valid():
        tag = form.cleaned_data.get("tag")
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
            return True, redirect(reverse(return_view_name, args=(the_object.pk,)))
    else:
        form = forms.CRMNoteForm()

    return False, render(request, "crm/note_create.html", locals())


@login_required
def create_note_for_user(request, user_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    user = get_object_or_404(User, pk=user_id)
    if request.site not in user.profile.sites.all():
        raise Http404()

    created, response = handle_create_note_for_object(
        request, user, "crm-user-details", "crm-user-note-update"
    )

    if created and user.profile and user.profile.organization:
        crm_users = get_users_with_perms(
            request.site, only_with_perms_in=["use_crm"]
        ).exclude(pk=request.user.pk)
        notify.send(
            sender=request.user,
            recipient=crm_users,
            verb="a créé une note de CRM",
            action_object=user,
            target=user.profile.organization,
            public=False,
            crm=True,
        )

    return response


@login_required
def create_note_for_project(request, project_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    project = get_object_or_404(Project.on_site, pk=project_id)

    _, response = handle_create_note_for_object(
        request, project, "crm-project-details", "crm-project-note-update"
    )

    return response


@login_required
def create_note_for_organization(request, organization_id):
    has_perm_or_403(request.user, "use_crm", request.site)

    qs = get_queryset_for_site_organizations(request.site)
    organization = get_object_or_404(qs, pk=organization_id)

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

    today = datetime.datetime.today().date()

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
