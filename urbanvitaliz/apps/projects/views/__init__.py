# encoding: utf-8

__all__ = ["rest", "feeds", "notes", "sharing", "tasks"]

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.survey import models as survey_models
from urbanvitaliz.utils import is_staff_or_403, is_switchtender_or_403

from .. import models, signals
from ..forms import OnboardingForm, PrivateNoteForm, ProjectForm
from ..utils import (can_administrate_or_403, can_administrate_project,
                     generate_ro_key, get_active_project,
                     refresh_user_projects_in_session, set_active_project_id)

########################################################################
# On boarding
########################################################################


def onboarding(request):
    """Return the onboarding page"""
    if request.method == "POST":
        form = OnboardingForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.emails.append(project.email)
            project.ro_key = generate_ro_key()
            postcode = form.cleaned_data.get("postcode")
            project.commune = geomatics.Commune.get_by_postal_code(postcode)
            project.save()
            models.Note(
                project=project,
                content=f"# Demande initiale\n\n{project.impediments}",
                public=True,
            ).save()

            signals.project_submitted.send(sender=models.Project, project=project)

            user, _ = auth.User.objects.get_or_create(
                username=project.email,
                defaults={
                    "email": project.email,
                    "first_name": form.cleaned_data.get("first_name"),
                    "last_name": form.cleaned_data.get("last_name"),
                },
            )
            log_user(request, user)

            response = redirect("survey-project-session", project_id=project.id)
            response["Location"] += "?first_time=1"
            return response
    else:
        form = OnboardingForm()
    return render(request, "projects/onboarding.html", locals())


########################################################################
# Switchtender
########################################################################


@login_required
@ensure_csrf_cookie
def project_list(request):
    """Return the projects for the switchtender"""
    is_switchtender_or_403(request.user)
    draft_projects = (
        models.Project.objects.in_departments(request.user.profile.departments.all())
        .filter(status="DRAFT")
        .order_by("-created_on")
    )
    return render(request, "projects/project/list.html", locals())


@login_required
def project_detail(request, project_id=None):
    """Return the details of given project for switchtender"""
    project = get_object_or_404(models.Project, pk=project_id)

    # check user can administrate projet (member or switchtender)
    if request.user.email != project.email:
        can_administrate_or_403(project, request.user)

    # Set this project as active
    set_active_project_id(request, project.pk)

    try:
        survey = survey_models.Survey.objects.get(pk=1)  # XXX Hardcoded survey ID
        session, created = survey_models.Session.objects.get_or_create(
            project=project, survey=survey
        )
    except survey_models.Survey.DoesNotExist:
        session = None

    can_administrate = can_administrate_project(project, request.user)
    can_administrate_draft = can_administrate_project(
        project, request.user, allow_draft=True
    )

    # Mark this project notifications unread
    project_ct = ContentType.objects.get_for_model(project)
    request.user.notifications.filter(
        target_content_type=project_ct.pk, target_object_id=project.pk
    ).mark_all_as_read()

    private_note_form = PrivateNoteForm()
    switchtenders = auth.User.objects.filter(
        tasks_created__in=project.tasks.all()
    ).distinct()

    return render(request, "projects/project/detail.html", locals())


def project_detail_from_sharing_link(request, project_ro_key):
    """Return a special view of the project using the sharing link"""
    try:
        project = models.Project.objects.filter(ro_key=project_ro_key)[0]
    except Exception:
        raise Http404()

    can_administrate = can_administrate_project(project, request.user)

    return render(request, "projects/project/detail-ro.html", locals())


@login_required
def project_update(request, project_id=None):
    """Update the base information of a project"""
    is_switchtender_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            instance = form.save(commit=False)
            postcode = form.cleaned_data.get("postcode")
            project.commune = geomatics.Commune.get_by_postal_code(postcode)
            instance.updated_on = timezone.now()
            instance.save()
            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        if project.commune:
            postcode = project.commune.postal
        else:
            postcode = None
        form = ProjectForm(instance=project, initial={"postcode": postcode})
    return render(request, "projects/project/update.html", locals())


@login_required
def project_accept(request, project_id=None):
    """Update project as accepted for processing"""
    is_switchtender_or_403(request.user)
    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.status = "TO_PROCESS"
        project.updated_on = timezone.now()
        project.save()
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
        active_project = models.Project.objects.filter(email=user.email).first()
        if active_project:
            set_active_project_id(request, active_project.id)


@login_required
def redirect_user_to_project(request):
    """Redirect user to project page given her context"""
    active_project = get_active_project(request)

    if active_project:
        return redirect(reverse("projects-project-detail", args=[active_project.id]))
    else:
        return redirect(reverse("home"))


# eof
