# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""


from django.contrib import messages
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from notifications import models as notifications_models

from urbanvitaliz.apps.communication import digests
from urbanvitaliz.apps.communication.api import send_email
from urbanvitaliz.apps.communication.digests import normalize_user_name
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.apps.onboarding import forms as onboarding_forms
from urbanvitaliz.apps.onboarding import models as onboarding_models
from urbanvitaliz.utils import (
    build_absolute_url,
    check_if_advisor,
    get_site_config_or_503,
    has_perm_or_403,
    is_staff_for_site,
    is_switchtender_or_403,
)

from .. import models, signals
from ..forms import SelectCommuneForm
from ..utils import (
    assign_advisor,
    assign_collaborator,
    assign_observer,
    can_administrate_project,
    generate_ro_key,
    get_active_project,
    is_advisor_for_project,
    is_project_moderator,
    is_project_moderator_or_403,
    is_regional_actor_for_project_or_403,
    refresh_user_projects_in_session,
    set_active_project_id,
    unassign_advisor,
)

__all__ = ["rest", "feeds", "notes", "sharing", "tasks", "documents"]

########################################################################
# On boarding
########################################################################


def create_project_prefilled(request):
    """Create a new project for someone else"""
    site_config = get_site_config_or_503(request.site)

    is_switchtender_or_403(request.user)

    form = onboarding_forms.OnboardingResponseForm(request.POST or None)
    onboarding_instance = onboarding_models.Onboarding.objects.get(
        pk=site_config.onboarding.pk
    )

    # Add fields in JSON to dynamic form rendering field.
    form.fields["response"].add_fields(onboarding_instance.form)

    if request.method == "POST":
        if form.is_valid():
            onboarding_response = form.save(commit=False)
            onboarding_response.onboarding = onboarding_instance

            project = models.Project()

            project.name = form.cleaned_data.get("name")
            project.phone = form.cleaned_data.get("phone")
            project.org_name = form.cleaned_data.get("org_name")
            project.description = form.cleaned_data.get("description")
            project.location = form.cleaned_data.get("location")
            project.postcode = form.cleaned_data.get("postcode")
            project.ro_key = generate_ro_key()
            project.status = "TO_PROCESS"
            project.submitted_by = request.user

            insee = form.cleaned_data.get("insee", None)
            if insee:
                project.commune = geomatics.Commune.get_by_insee_code(insee)
            else:
                postcode = form.cleaned_data.get("postcode")
                project.commune = geomatics.Commune.get_by_postal_code(postcode)

            project.save()
            project.sites.add(request.site)

            onboarding_response.project = project
            onboarding_response.save()

            user, created = auth.User.objects.get_or_create(
                username=form.cleaned_data.get("email"),
                defaults={
                    "email": form.cleaned_data.get("email"),
                    "first_name": form.cleaned_data.get("first_name"),
                    "last_name": form.cleaned_data.get("last_name"),
                },
            )

            user.profile.sites.add(request.site)

            assign_collaborator(user, project, is_owner=True)

            # Add the current user as an advisor
            assign_advisor(request.user, project, request.site)

            markdown_content = render_to_string(
                "projects/project/onboarding_initial_note.md",
                {
                    "onboarding_response": onboarding_response,
                    "project": project,
                },
            )

            models.Note(
                project=project,
                content=(
                    "# Demande initiale\n\n"
                    f"{project.description}\n\n"
                    f"{ markdown_content }"
                ),
                public=True,
                site=request.site,
            ).save()

            invite, _ = invites_models.Invite.objects.get_or_create(
                project=project,
                inviter=request.user,
                site=request.site,
                email=user.email,
                defaults={
                    "message": (
                        "Je viens de déposer votre projet sur la"
                        "plateforme de manière à faciliter nos échanges."
                    )
                },
            )
            send_email(
                template_name="sharing invitation",
                recipients=[{"email": user.email}],
                params={
                    "sender": {"email": request.user.email},
                    "message": invite.message,
                    "invite_url": build_absolute_url(
                        invite.get_absolute_url(),
                        auto_login_user=user if not created else None,
                    ),
                    "project": digests.make_project_digest(project),
                },
            )

            messages.success(
                request,
                (
                    "Un courriel d'invitation à rejoindre"
                    f" le projet a été envoyé à {user.email}."
                ),
                extra_tags=["email"],
            )

            signals.project_submitted.send(
                sender=models.Project,
                site=request.site,
                submitter=user,
                project=project,
            )

            # NOTE check if commune is unique for code postal
            if project.commune:
                communes = geomatics.Commune.objects.filter(
                    postal=project.commune.postal
                )
                if communes.count() > 1:
                    url = reverse(
                        "projects-onboarding-select-commune", args=[project.id]
                    )
                    return redirect(url)

            return redirect("projects-project-detail-knowledge", project_id=project.id)

    return render(request, "projects/project/create_prefilled.html", locals())


@login_required
def select_commune(request, project_id=None):
    """Intermediate screen to select proper insee number of commune"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    response = redirect("survey-project-session", project_id=project.id)
    response["Location"] += "?first_time=1"
    if not project.commune:
        return response
    communes = geomatics.Commune.objects.filter(postal=project.commune.postal)
    if request.method == "POST":
        form = SelectCommuneForm(communes, request.POST)
        if form.is_valid():
            project.commune = form.cleaned_data["commune"]
            project.save()
            return response
    else:
        form = SelectCommuneForm(communes)
    return render(request, "projects/select-commune.html", locals())


########################################################################
# Switchtender
########################################################################
def mark_general_notifications_as_seen(user):
    # Mark some notifications as seen
    project_ct = ContentType.objects.get_for_model(models.Project)
    notifications = user.notifications.unread().filter(
        Q(verb="a déposé le projet") | Q(verb="a soumis pour modération le projet"),
        target_content_type=project_ct.pk,
    )
    notifications.mark_all_as_read()


@login_required
def project_list(request):
    if is_staff_for_site(request.user, request.site):
        return redirect("projects-project-list-staff")

    if check_if_advisor(request.user, request.site) or can_administrate_project(
        project=None, user=request.user
    ):
        return redirect("projects-project-list-advisor")

    raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")


@login_required
@ensure_csrf_cookie
@never_cache
def project_list_for_advisor(request):
    """Return the projects for the advisor"""
    if not (
        check_if_advisor(request.user, request.site)
        or can_administrate_project(project=None, user=request.user)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    # unread_notifications = notifications_models.Notification.on_site.unread().filter(
    #    recipient=request.user, public=True
    # )

    mark_general_notifications_as_seen(request.user)

    project_ct = ContentType.objects.get_for_model(models.Project)
    user_project_pks = list(
        request.user.project_states.filter(
            project__switchtenders=request.user
        ).values_list("project__pk", flat=True)
    )

    action_stream = (
        request.user.notifications.filter(
            target_content_type=project_ct,
            target_object_id__in=user_project_pks,
        )
        .prefetch_related("actor__profile__organization")
        .prefetch_related("action_object")
        .prefetch_related("target")
        .order_by("-timestamp")[:20]
    )

    return render(request, "projects/project/personal_advisor_dashboard.html", locals())


@login_required
@ensure_csrf_cookie
def project_list_for_staff(request):
    """
    Return the projects for the staff (and for other people as a fallback until the
    new dashboard is fully completed).
    """
    if not (
        check_if_advisor(request.user, request.site)
        or can_administrate_project(project=None, user=request.user)
        or is_staff_for_site(request.user, request.site)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    project_moderator = is_project_moderator(request.user, request.site)

    draft_projects = []
    if project_moderator:
        draft_projects = models.Project.on_site.filter(status="DRAFT").order_by(
            "-created_on"
        )

    unread_notifications = (
        notifications_models.Notification.on_site.unread()
        .filter(recipient=request.user, public=True)
        .prefetch_related("actor__profile__organization")
        .prefetch_related("action_object")
        .prefetch_related("target")
        .order_by("-timestamp")[:100]
    )

    mark_general_notifications_as_seen(request.user)

    return render(request, "projects/project/list-kanban.html", locals())


@login_required
@ensure_csrf_cookie
def project_maplist(request):
    """Return the projects for the switchtender as a map"""
    if not (
        check_if_advisor(request.user)
        or can_administrate_project(project=None, user=request.user)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    project_moderator = is_project_moderator(request.user, request.site)

    draft_projects = []
    if is_project_moderator:
        draft_projects = (
            models.Project.on_site.in_departments(
                request.user.profile.departments.all()
            )
            .filter(status="DRAFT")
            .order_by("-created_on")
        )

    unread_notifications = (
        notifications_models.Notification.on_site.unread()
        .filter(recipient=request.user, public=True)
        .prefetch_related("actor__profile__organization")
        .prefetch_related("action_object")
        .prefetch_related("target")
        .order_by("-timestamp")[:100]
    )

    return render(request, "projects/project/list-map.html", locals())


@login_required
def project_accept(request, project_id=None):
    """Update project as accepted for processing"""
    is_project_moderator_or_403(request.user, request.site)

    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.status = "TO_PROCESS"
        project.updated_on = timezone.now()
        project.save()

        signals.project_validated.send(
            sender=models.Project,
            site=request.site,
            moderator=request.user,
            project=project,
        )

        owner = project.owner
        if owner:
            # Update owner permissions now the project is no in DRAFT state anymore
            assign_collaborator(owner, project, is_owner=True)

            # Send an email to the project owner
            params = {
                "project": digests.make_project_digest(project, owner),
            }
            send_email(
                template_name="project_accepted",
                recipients=[
                    {
                        "name": normalize_user_name(owner),
                        "email": project.owner.email,
                    }
                ],
                params=params,
            )

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_switchtender_join(request, project_id=None):
    """Join as switchtender"""

    project = get_object_or_404(models.Project, pk=project_id)

    if not can_administrate_project(project, request.user):
        is_regional_actor_for_project_or_403(
            get_current_site(request), project, request.user, allow_national=True
        )

    if request.method == "POST":
        assign_advisor(request.user, project)

        personal_status, created = models.UserProjectStatus.objects.get_or_create(
            site=request.site,
            user=request.user,
            project=project,
            defaults={"status": "TODO"},
        )
        if not created:
            personal_status.status = "TODO"
            personal_status.save()

        project.updated_on = timezone.now()
        project.save()

        signals.project_switchtender_joined.send(sender=request.user, project=project)

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_observer_join(request, project_id=None):
    """Join as observer"""
    project = get_object_or_404(models.Project, pk=project_id)

    if not can_administrate_project(project, request.user):
        is_regional_actor_for_project_or_403(
            get_current_site(request), project, request.user, allow_national=True
        )

    if request.method == "POST":
        assign_observer(request.user, project)

        personal_status, created = models.UserProjectStatus.objects.get_or_create(
            site=request.site,
            user=request.user,
            project=project,
            defaults={"status": "TODO"},
        )
        if not created:
            personal_status.status = "TODO"
            personal_status.save()

        project.updated_on = timezone.now()
        project.save()

        signals.project_observer_joined.send(sender=request.user, project=project)

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_switchtender_leave(request, project_id=None):
    """Leave switchtender"""
    project = get_object_or_404(models.Project, pk=project_id)

    if not is_advisor_for_project(request.user, project):
        raise PermissionDenied()

    if request.method == "POST":
        unassign_advisor(request.user, project)
        project.updated_on = timezone.now()
        project.save()

        personal_status, created = models.UserProjectStatus.objects.get_or_create(
            site=request.site,
            user=request.user,
            project=project,
            defaults={"status": "NOT_INTERESTED"},
        )
        if not created:
            personal_status.status = "NOT_INTERESTED"
            personal_status.save()

        signals.project_switchtender_leaved.send(sender=request.user, project=project)

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_delete(request, project_id=None):
    """Mark project as deleted in the DB"""
    has_perm_or_403(request.user, "sites.delete_projects", request.site)

    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.deleted = project.updated_on = timezone.now()
        project.save()
    return redirect(reverse("projects-project-list"))


########################################################################
# Login methods and signals
########################################################################
@receiver(user_logged_in)
def post_login_set_active_project(sender, user, request, **kwargs):
    # store my projects in the session
    refresh_user_projects_in_session(request, user)

    # Needed since get_active_project expects a user attribute
    request.user = user

    active_project = get_active_project(request)

    if not active_project:
        # Try to fetch a project
        active_project = models.Project.on_site.filter(members=user).first()
        if active_project:
            set_active_project_id(request, active_project.id)


# eof
