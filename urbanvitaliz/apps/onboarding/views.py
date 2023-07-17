# encoding: utf-8

"""
views for onboarding new users/projects

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-17 20:39:35 CEST
"""

from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.contrib.sites import models as sites
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.http import urlencode
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.communication import digests
from urbanvitaliz.apps.communication.api import send_email
from urbanvitaliz.apps.communication.digests import normalize_user_name
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects import models as projects
from urbanvitaliz.apps.projects import signals as projects_signals
from urbanvitaliz.apps.projects.utils import generate_ro_key, assign_collaborator
from urbanvitaliz.utils import get_site_config_or_503


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

        user, new_user = auth.User.objects.get_or_create(
            username=email, defaults={"email": email}
        )

        if not new_user and not request.user.is_authenticated:
            # user exists but is not currently logged in,
            # save data, log in, and come back to complete
            request.session["onboarding_existing_data"] = form.cleaned_data
            login_url = reverse("account_login")
            next_args = urlencode({"next": reverse("projects-onboarding")})
            return redirect(f"{login_url}?{next_args}")

        user = update_user(request.site, user, form.cleaned_data)

        project = create_project_for_user(user, form.cleaned_data, "DRAFT")

        project.sites.add(request.site)

        onboarding_response = form.save(commit=False)
        onboarding_response.onboarding = onboarding_instance
        onboarding_response.project = project
        onboarding_response.save()

        create_initial_note(request.site, onboarding_response)

        notify_and_email_new_project(request.site, project, user)

        # cleanup now useless onboarding existing data if present
        if "onboarding_existing_data" in request.session:
            del request.session["onboarding_existing_data"]

        if new_user:
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


def create_project_for_user(
    user: auth.User, data: dict, status: str
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
        submitted_by=user,
        name=data.get("name"),
        phone=data.get("phone"),
        org_name=data.get("org_name"),
        description=data.get("description"),
        location=data.get("location"),
        commune=commune,
        status=status,
        ro_key=generate_ro_key(),
    )

    assign_collaborator(user, project, is_owner=True)

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


def get_organization(site: sites.Site, name: str) -> addressbook_models.Organization:
    """Return (new) organization with the given name or None"""
    if not name:
        return None
    organization = addressbook_models.Organization.get_or_create(name)
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
            f"# Demande initiale\n\n{project.description}\n\n{ markdown_content }"
        ),
        public=True,
        site=site,
    )


def notify_and_email_new_project(
    site: sites.Site, project: projects.Project, user: auth.User
) -> None:
    """Send notifications and email for new project"""

    # notify project submission
    projects_signals.project_submitted.send(
        sender=projects.Project,
        site=site,
        submitter=user,
        project=project,
    )

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


# eof
