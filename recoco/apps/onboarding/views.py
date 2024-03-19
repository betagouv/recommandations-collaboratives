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

from recoco.apps.addressbook import models as addressbook
from recoco.apps.communication import digests
from recoco.apps.communication.api import send_email
from recoco.apps.communication.digests import normalize_user_name
from recoco.apps.geomatics import models as geomatics
from recoco.apps.invites import models as invites
from recoco.apps.projects import models as projects
from recoco.apps.projects import signals as projects_signals
from recoco.apps.projects.utils import (
    assign_advisor,
    assign_collaborator,
    generate_ro_key,
    refresh_user_projects_in_session,
)
from recoco.apps.survey.forms import AnswerForm

from recoco.utils import (
    build_absolute_url,
    get_site_config_or_503,
    is_switchtender_or_403,
)

from . import forms, models

########################################################################
# User driven onboarding for a new project
########################################################################


def onboarding(request):
    """Depending on the user login, redirect to next page"""

    if request.user.is_authenticated:
        return redirect("projects-onboarding-project")

    form = forms.ModalOnboardingEmailForm(request.POST)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]

        try:
            user = auth.User.objects.get(username=email)
        except auth.User.DoesNotExist:
            user = None

        request.session["onboarding_email"] = email

        if user:
            # User have already an account but is disconnected
            return redirect(reverse("projects-onboarding-signin"))

    return redirect(reverse("projects-onboarding-signup"))


########################################################################
# User driven onboarding for a new project
########################################################################


def onboarding_signup(request):
    """Return the onboarding signup page and process onboarding signup submission"""

    existing_email_user = request.session.get("onboarding_email")

    form = forms.OnboardingSignupForm(
        request.POST or None, initial={"email": existing_email_user}
    )

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data.get("email").lower()

        user, is_new_user = auth.User.objects.get_or_create(
            username=email, defaults={"email": email}
        )
        log_user(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(f"{reverse('projects-onboarding-project')}")

    context = {"form": form}
    return render(request, "onboarding/onboarding-signup.html", context)


def onboarding_signin(request):
    """Return the onboarding signin page and process onboarding signin submission"""

    existing_data = request.session.get("onboarding_existing_data")

    form = forms.OnboardingSigninForm(request.POST or None, initial=existing_data)

    if request.method == "POST":
        # FIXME with signin logic
        # and form.is_valid():
        # NOTE we may check for known user not logged before valid form
        # email = (
        #     request.user.username
        #     if request.user.is_authenticated
        #     else form.cleaned_data.get("email").lower()
        # )

        # user, is_new_user = auth.User.objects.get_or_create(
        #     username=email, defaults={"email": email}
        # )
        return redirect(f"{reverse('projects-onboarding-project')}")

    context = {"form": form}
    return render(request, "onboarding/onboarding-signin.html", context)


@login_required
def onboarding_project(request):
    """Return the onboarding page and process onboarding submission"""
    site_config = get_site_config_or_503(request.site)

    # Fetch the onboarding form associated with the current site
    form = forms.OnboardingProjectForm(request.POST or None)

    question_forms = []
    for question in site_config.onboarding_questions.all():
        form_prefix = f"q{question.id}-"
        question_forms.append(
            AnswerForm(
                question,
                None,
                request.POST or None,
                prefix=form_prefix,
            )
        )

    if request.method == "POST":

        all_forms_valid = form.is_valid()

        for question_form in question_forms:
            all_forms_valid = all_forms_valid and question.is_valid()

        if all_forms_valid:
            # FIXME
            project = create_project_for_user(
                user=request.user, data=form.cleaned_data, status="DRAFT"
            )

            project.sites.add(request.site)

            # Save survey questions
            for question_form in question_forms:
                question.save()

            assign_collaborator(request.user, project, is_owner=True)

            notify_new_project(request.site, project, request.user)
            email_owner_of_project(request.site, project, request.user)

            refresh_user_projects_in_session(request, request.user)

            return redirect(
                f"{reverse('projects-onboarding-summary', args=(project.pk,))}"
            )

    context = {
        "form": form,
        "question_forms": question_forms,
    }
    return render(request, "onboarding/onboarding-project.html", context)


@login_required
def onboarding_summary(request, project_id=None):
    """Resume project from onboarding"""

    # if we're back from login page restore data already entered
    project = get_object_or_404(projects.Project, sites=request.site, pk=project_id)
    # TODO redirect EDL ?
    # action_button_form_param = {
    #     "submit": {
    #         "label": "Suivant",
    #     },
    #     "cancel": {"label": "Précédent", "href": reverse("projects-onboarding-signup")},
    # }

    context = {"project": project}
    return render(request, "onboarding/onboarding-summary.html", context)


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
