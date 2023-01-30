# encoding: utf-8

__all__ = ["rest", "feeds", "notes", "sharing", "tasks", "documents"]

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""


from django.contrib import messages
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from notifications import models as notifications_models
from urbanvitaliz.apps.communication import digests
from urbanvitaliz.apps.communication.api import send_email
from urbanvitaliz.apps.communication.digests import normalize_user_name
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.apps.onboarding import forms as onboarding_forms
from urbanvitaliz.apps.onboarding import models as onboarding_models
from urbanvitaliz.utils import (build_absolute_url, check_if_switchtender,
                                get_site_config_or_503, is_staff_or_403,
                                is_switchtender_or_403)

from .. import models, signals
from ..forms import SelectCommuneForm
from ..utils import (can_administrate_or_403, can_administrate_project,
                     generate_ro_key, get_active_project, is_project_moderator,
                     is_project_moderator_or_403,
                     is_regional_actor_for_project_or_403,
                     refresh_user_projects_in_session, set_active_project_id)

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

            models.ProjectMember.objects.create(
                member=user, project=project, is_owner=True
            )

            # Add the current user as switchtender
            project.switchtenders_on_site.create(
                switchtender=request.user, site=request.site
            )

            markdown_content = render_to_string(
                "projects/project/onboarding_initial_note.md",
                {
                    "onboarding_response": onboarding_response,
                    "project": project,
                },
            )

            models.Note(
                project=project,
                content=f"# Demande initiale\n\n{project.description}\n\n{ markdown_content }",
                public=True,
            ).save()

            invite, _ = invites_models.Invite.objects.get_or_create(
                project=project,
                inviter=request.user,
                site=request.site,
                email=user.email,
                defaults={
                    "message": "Je viens de déposer votre projet sur la plateforme de manière à faciliter nos échanges."
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
                "Un courriel d'invitation à rejoindre le projet a été envoyé à {0}.".format(
                    user.email
                ),
                extra_tags=["email"],
            )

            signals.project_submitted.send(
                sender=models.Project, submitter=user, project=project
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


@login_required
def project_list(request):
    if not (
        check_if_switchtender(request.user)
        or can_administrate_project(project=None, user=request.user)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    if request.user.is_staff:
        return redirect("projects-project-list-staff")

    return redirect("projects-project-list-advisor")


@login_required
@ensure_csrf_cookie
def project_list_for_advisor(request):
    """Return the projects for the advisor"""
    if not (
        check_if_switchtender(request.user)
        or can_administrate_project(project=None, user=request.user)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    project_moderator = is_project_moderator(request.user)

    draft_projects = []
    if is_project_moderator:
        draft_projects = (
            models.Project.on_site.in_departments(
                request.user.profile.departments.all()
            )
            .filter(status="DRAFT")
            .order_by("-created_on")
        )

    unread_notifications = notifications_models.Notification.on_site.unread().filter(
        recipient=request.user, public=True
    )

    return render(request, "projects/project/advisor_dashboard.html", locals())


@login_required
@ensure_csrf_cookie
def project_list_for_staff(request):
    """Return the projects for the staff"""
    if not (
        check_if_switchtender(request.user)
        or can_administrate_project(project=None, user=request.user)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    project_moderator = is_project_moderator(request.user)

    draft_projects = []
    if is_project_moderator:
        draft_projects = (
            models.Project.on_site.in_departments(
                request.user.profile.departments.all()
            )
            .filter(status="DRAFT")
            .order_by("-created_on")
        )

    unread_notifications = notifications_models.Notification.on_site.unread().filter(
        recipient=request.user, public=True
    )

    return render(request, "projects/project/list-kanban.html", locals())


@login_required
@ensure_csrf_cookie
def project_maplist(request):
    """Return the projects for the switchtender as a map"""
    if not (
        check_if_switchtender(request.user)
        or can_administrate_project(project=None, user=request.user)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    project_moderator = is_project_moderator(request.user)

    draft_projects = []
    if is_project_moderator:
        draft_projects = (
            models.Project.on_site.in_departments(
                request.user.profile.departments.all()
            )
            .filter(status="DRAFT")
            .order_by("-created_on")
        )

    unread_notifications = notifications_models.Notification.on_site.unread().filter(
        recipient=request.user, public=True
    )

    return render(request, "projects/project/list-map.html", locals())


@login_required
def project_accept(request, project_id=None):
    """Update project as accepted for processing"""
    is_project_moderator_or_403(request.user)

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

        if project.owner:
            # Send an email to the project owner
            params = {
                "project": digests.make_project_digest(project, project.owner),
            }
            send_email(
                template_name="project_accepted",
                recipients=[
                    {
                        "name": normalize_user_name(project.owner),
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
        switchtending, created = project.switchtenders_on_site.get_or_create(
            switchtender=request.user,
            site=request.site,
            defaults={"is_observer": False},
        )
        if not created:
            switchtending.is_observer = False
            switchtending.save()

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
        switchtending, created = project.switchtenders_on_site.get_or_create(
            switchtender=request.user, site=request.site, defaults={"is_observer": True}
        )
        if not created:
            switchtending.is_observer = True
            switchtending.save()

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
    can_administrate_or_403(project, request.user)

    if request.method == "POST":
        project.switchtenders_on_site.filter(switchtender=request.user).delete()
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
    is_staff_or_403(request.user)
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
