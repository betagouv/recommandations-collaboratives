# encoding: utf-8

"""
views for onboarding new users/projects

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-17 20:39:35 CEST
"""

from django.contrib import messages
from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites import models as sites
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.http import urlencode

from urbanvitaliz.apps.addressbook import models as addressbook
from urbanvitaliz.apps.communication import digests
from urbanvitaliz.apps.communication.api import send_email
from urbanvitaliz.apps.communication.digests import normalize_user_name
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.invites import models as invites
from urbanvitaliz.apps.projects import models as projects
from urbanvitaliz.apps.projects import signals as projects_signals
from urbanvitaliz.apps.projects.utils import (
    assign_advisor,
    assign_collaborator,
    generate_ro_key,
)
from urbanvitaliz.utils import (
    build_absolute_url,
    get_site_config_or_503,
    is_switchtender_or_403,
)

from . import forms, models

########################################################################
# User driven onboarding for a new project
########################################################################


def onboarding(request):
    """Return the onboarding page and process onboarding submission"""

    site_config = get_site_config_or_503(request.site)

    # if we're back from login page restore data already entered
    existing_data = request.session.get("onboarding_existing_data")

    # Fetch the onboarding form associated with the current site
    form = forms.OnboardingResponseWithCaptchaForm(
        request.POST or None, initial=existing_data
    )

    onboarding_instance = models.Onboarding.objects.get(pk=site_config.onboarding.pk)

    # Add fields in JSON to dynamic form rendering field.
    form.fields["response"].add_fields(onboarding_instance.form)

    if request.method == "POST" and form.is_valid():
        # NOTE we may check for known user not logged before valid form
        email = (
            request.user.username
            if request.user.is_authenticated
            else form.cleaned_data.get("email").lower()
        )

        user, is_new_user = auth.User.objects.get_or_create(
            username=email, defaults={"email": email}
        )

        if not is_new_user and not request.user.is_authenticated:
            # user exists but is not currently logged in,
            # save data, log in, and come back to complete
            request.session["onboarding_existing_data"] = form.cleaned_data
            login_url = reverse("account_login")
            next_args = urlencode({"next": reverse("projects-onboarding")})
            return redirect(f"{login_url}?{next_args}")

        user = update_user(request.site, user, form.cleaned_data)

        project = create_project_for_user(
            user=user, data=form.cleaned_data, status="DRAFT"
        )

        project.sites.add(request.site)

        onboarding_response = form.save(commit=False)
        onboarding_response.onboarding = onboarding_instance
        onboarding_response.project = project
        onboarding_response.save()

        assign_collaborator(user, project, is_owner=True)

        create_initial_note(request.site, onboarding_response)

        notify_new_project(request.site, project, user)
        email_owner_of_project(request.site, project, user)

        # cleanup now useless onboarding existing data if present
        if "onboarding_existing_data" in request.session:
            del request.session["onboarding_existing_data"]

        if is_new_user:
            # new user first have to setup her password and then complete the survey
            log_user(request, user, backend="django.contrib.auth.backends.ModelBackend")
            next_url = (
                reverse("survey-project-session", args=(project.id,)) + "?first_time=1"
            )
            next_args = urlencode({"next": next_url})
            return redirect(f"{reverse('home-user-setup-password')}?{next_args}")
        else:
            response = redirect("survey-project-session", project_id=project.id)
            response["Location"] += "?first_time=1"
            return response

    return render(request, "onboarding/onboarding.html", locals())


########################################################################
# Advisor onboard someone else
########################################################################


def create_project_prefilled(request):
    """Create a new project for someone else"""
    site_config = get_site_config_or_503(request.site)

    is_switchtender_or_403(request.user)

    form = forms.OnboardingResponseForm(request.POST or None)
    onboarding_instance = models.Onboarding.objects.get(pk=site_config.onboarding.pk)

    # Add fields in JSON to dynamic form rendering field.
    form.fields["response"].add_fields(onboarding_instance.form)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data.get("email").lower()

        user, is_new_user = auth.User.objects.get_or_create(
            username=email, defaults={"email": email}
        )
        user = update_user(request.site, user, form.cleaned_data)

        project = create_project_for_user(
            user=user,
            data=form.cleaned_data,
            status="TO_PROCESS",
            submitted_by=request.user,
        )

        project.sites.add(request.site)

        onboarding_response = form.save(commit=False)
        onboarding_response.onboarding = onboarding_instance
        onboarding_response.project = project
        onboarding_response.save()

        assign_collaborator(user, project, is_owner=True)
        assign_advisor(request.user, project, request.site)

        create_initial_note(request.site, onboarding_response)

        invite_user_to_project(request, user, project, is_new_user)
        notify_new_project(request.site, project, user)

        return redirect("projects-project-detail-knowledge", project_id=project.id)

    return render(request, "onboarding/prefill.html", locals())


@login_required
def select_commune(request, project_id=None):
    """Intermediate screen to select proper insee number of commune"""
    project = get_object_or_404(projects.Project, sites=request.site, pk=project_id)
    response = redirect("survey-project-session", project_id=project.id)
    response["Location"] += "?first_time=1"
    if not project.commune:
        return response
    communes = geomatics.Commune.objects.filter(postal=project.commune.postal)
    if request.method == "POST":
        form = forms.SelectCommuneForm(communes, request.POST)
        if form.is_valid():
            project.commune = form.cleaned_data["commune"]
            project.save()
            return response
    else:
        form = forms.SelectCommuneForm(communes)
    return render(request, "onboarding/select-commune.html", locals())


def create_project_for_user(
    user: auth.User, data: dict, status: str, submitted_by: auth.User = None
) -> projects.Project:
    """Use data from form to create and return a new project for user"""

    insee = data.get("insee", None)
    postcode = data.get("postcode")

    commune = (
        geomatics.Commune.get_by_insee_code(insee)
        if insee
        else geomatics.Commune.get_by_postal_code(postcode)
    )

    project = projects.Project.objects.create(
        submitted_by=submitted_by or user,
        name=data.get("name"),
        phone=data.get("phone"),
        org_name=data.get("org_name"),
        description=data.get("description"),
        location=data.get("location"),
        commune=commune,
        status=status,
        ro_key=generate_ro_key(),
    )

    return project


def update_user(site: sites.Site, user: auth.User, data: dict) -> auth.User:
    """Update and return given user and its profile w/ data from form"""

    # FIXME existing value are kept instead of new ones, why?

    user.first_name = user.first_name or data.get("first_name")
    user.last_name = user.last_name or data.get("last_name")
    user.save()

    organization = get_organization(site, data.get("org_name"))

    profile = user.profile
    profile.organization = profile.organization or organization
    profile.phone_no = profile.phone_no or data.get("phone")
    profile.save()

    profile.sites.add(site)

    return user


def get_organization(site: sites.Site, name: str) -> addressbook.Organization:
    """Return (new) organization with the given name or None"""
    if not name:
        return None
    organization = addressbook.Organization.get_or_create(name)
    organization.sites.add(site)
    return organization


def create_initial_note(
    site: sites.Site, onboarding_response: models.OnboardingResponse
) -> None:
    """Create the initial note that describe the project"""

    project = onboarding_response.project

    markdown_content = render_to_string(
        "projects/project/onboarding_initial_note.md",
        {
            "onboarding_response": onboarding_response,
            "project": project,
        },
    )

    projects.Note.objects.create(
        project=project,
        content=(
            f"# Demande initiale\n\n"
            f"{project.description}\n\n"
            f"{ markdown_content }"
        ),
        public=True,
        site=site,
    )


def notify_new_project(
    site: sites.Site, project: projects.Project, owner: auth.User
) -> None:
    """Create notification of new project"""

    # notify project submission
    projects_signals.project_submitted.send(
        sender=projects.Project,
        site=site,
        submitter=owner,
        project=project,
    )


def email_owner_of_project(
    site: sites.Site, project: projects.Project, user: auth.User
) -> None:
    """Send email to new project owner"""

    # Send an email to the project owner
    params = {
        "project": digests.make_project_digest(
            project, project.owner, url_name="knowledge"
        ),
    }
    send_email(
        template_name="project_received",
        recipients=[
            {
                "name": normalize_user_name(project.owner),
                "email": project.owner.email,
            }
        ],
        params=params,
    )
    # FIXME return send_mail status ?


def invite_user_to_project(
    request, user: auth.User, project: projects.Project, is_new_user: bool
):
    invite, _ = invites.Invite.objects.get_or_create(
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
                auto_login_user=user if not is_new_user else None,
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


# eof
