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
from django.views.generic import FormView

from recoco.apps.addressbook import models as addressbook
from recoco.apps.communication import constants as communication_constants
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


class OnboardingView(FormView):
    """Dispatch user based on auth/provided credentials"""

    form_class = forms.OnboardingEmailForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("projects-onboarding-project"))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return redirect(reverse("account_login"))

    def form_valid(self, form):
        self.request.session["onboarding_email"] = form.cleaned_data["email"]

        try:
            auth.User.objects.get(email=form.cleaned_data["email"])
            next_args = urlencode({"next": reverse("projects-onboarding-project")})
            login_url = reverse("account_login")
            return redirect(f"{login_url}?{next_args}")
        except auth.User.DoesNotExist:
            signup_url = reverse("projects-onboarding-signup")
            return redirect(signup_url)

    def form_invalid(self, form):
        return redirect(reverse("account_login"))


def onboarding_signup(request):
    """Return the onboarding signup page and process onboarding signup submission"""

    if request.user.is_authenticated:
        return redirect(reverse("projects-onboarding-project"))
    # FIXME existing email is not kept in form
    existing_email_user = request.session.get("onboarding_email")

    form = forms.OnboardingSignupForm(
        request.POST or None, initial={"email": existing_email_user}
    )

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data.get("email").lower()

        user, is_new_user = auth.User.objects.get_or_create(
            username=email,
            first_name=form.cleaned_data.get("first_name"),
            last_name=form.cleaned_data.get("last_name"),
            defaults={"email": email},
        )

        if not is_new_user:
            # user exists but is not currently logged in,
            login_url = reverse("account_login")
            next_args = urlencode({"next": reverse("projects-onboarding-project")})
            return redirect(f"{login_url}?{next_args}")

        user.set_password(form.cleaned_data.get("password"))
        user = update_user(
            request.site,
            user,
            form.cleaned_data.get("first_name"),
            form.cleaned_data.get("last_name"),
            form.cleaned_data.get("org_name"),
            form.cleaned_data.get("phone"),
        )

        log_user(request, user, backend="django.contrib.auth.backends.ModelBackend")

        if "onboarding_email" in request.session:
            del request.session["onboarding_email"]

        return redirect(f"{reverse('projects-onboarding-project')}")

    context = {"form": form}
    return render(request, "onboarding/onboarding-signup.html", context)


@login_required
def onboarding_project(request):
    """Return the onboarding page and process onboarding submission"""
    site_config = get_site_config_or_503(request.site)

    form = forms.OnboardingProject(request.POST or None)
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
            all_forms_valid = all_forms_valid and question_form.is_valid()

        if all_forms_valid:
            project_dict = {
                "name": form.cleaned_data["name"],
                "location": form.cleaned_data["location"],
                "insee": form.cleaned_data["insee"],
                "description": form.cleaned_data["description"],
            }

            project = create_project_for_user(
                user=request.user, data=project_dict, status="DRAFT"
            )

            project.sites.add(request.site)

            # Save survey questions
            for question_form in question_forms:
                question.save()

            assign_collaborator(request.user, project, is_owner=True)

            # FIXME adapt function
            # create_initial_note(request.site, onboarding_response)
            notify_new_project(request.site, project, request.user)
            email_owner_of_project(request.site, project, request.user)

            refresh_user_projects_in_session(request, request.user)

            # cleanup now useless onboarding existing data if present
            if "onboarding_signup" in request.session:
                del request.session["onboarding_signup"]

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

    project = get_object_or_404(projects.Project, sites=request.site, pk=project_id)
    next_args_for_project_location = urlencode(
        {"next": reverse("survey-project-session", args=(project.pk,))}
    )
    next_url = f"{reverse('projects-project-location', args=(project.pk,))}?{next_args_for_project_location}"

    context = {"project": project, "next_url": next_url}
    return render(request, "onboarding/onboarding-summary.html", context)


########################################################################
# Advisor onboard someone else
########################################################################


# TODO to delete when prefill v2 is deploy
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
        user = update_user(
            request.site,
            user,
            form.cleaned_data.get("first_name"),
            form.cleaned_data.get("last_name"),
            form.cleaned_data.get("org_name"),
            form.cleaned_data.get("phone"),
        )

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
def create_user_for_project_prefilled(request):
    """Create a new project for someone else - step 1 create user"""
    # site_config = get_site_config_or_503(request.site)

    is_switchtender_or_403(request.user)

    prefill_signup_user_data = request.session.get("prefill_signup_user")

    # FIXME make this form initializable
    form = forms.PrefillSignupForm(
        request.POST or None, initial=prefill_signup_user_data
    )

    if request.method == "POST" and form.is_valid():
        request.session["prefill_signup_user"] = form.cleaned_data

        return redirect(f"{reverse('projects-project-prefill-project')}")

    return render(request, "onboarding/prefill-user.html", locals())


@login_required
def create_project_for_project_prefilled(request):
    """Create a new project for someone else - step 2 create project"""
    site_config = get_site_config_or_503(request.site)

    is_switchtender_or_403(request.user)

    prefill_signup_user_data = request.session.get("prefill_signup_user")

    if not prefill_signup_user_data:
        return redirect(f"{reverse('projects-project-prefill-signup')}")

    form = forms.PrefillProjectForm(request.POST or None)

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
            all_forms_valid = all_forms_valid and question_form.is_valid()

        if all_forms_valid:
            project_dict = {
                "name": form.cleaned_data["name"],
                "location": form.cleaned_data["location"],
                "insee": form.cleaned_data["insee"],
                "org_name": request.user.profile.organization,
                "phone": request.user.profile.phone_no,
                "description": form.cleaned_data["description"],
            }

            # User creation
            email = prefill_signup_user_data.get("email").lower()

            user, is_new_user = auth.User.objects.get_or_create(
                username=email, defaults={"email": email}
            )

            if is_new_user:
                user = update_user(
                    site=request.site,
                    user=user,
                    first_name=prefill_signup_user_data.get("first_name"),
                    last_name=prefill_signup_user_data.get("last_name"),
                    org_name=prefill_signup_user_data.get("org_name"),
                    phone=prefill_signup_user_data.get("phone"),
                )

            # Project creation

            project = create_project_for_user(
                user=request.user, data=project_dict, status="DRAFT"
            )

            project.sites.add(request.site)

            # Save survey questions
            for question_form in question_forms:
                question.save()

            assign_collaborator(user, project, is_owner=True)
            assign_advisor(request.user, project, request.site)

            # FIXME adapt function
            # create_initial_note(request.site, onboarding_response)

            invite_user_to_project(request, user, project, is_new_user)
            notify_new_project(request.site, project, user)

            # cleanup now useless prefill existing data if present
            if "prefill_signup_user" in request.session:
                del request.session["prefill_signup_user"]

            return redirect(
                f"{reverse('projects-onboarding-summary', args=(project.pk,))}"
            )

    return render(request, "onboarding/prefill-project.html", locals())


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
        description=data.get("description"),
        location=data.get("location"),
        commune=commune,
        status=status,
        ro_key=generate_ro_key(),
    )

    return project


def update_user(
    site: sites.Site,
    user: auth.User,
    first_name: str,
    last_name: str,
    org_name: str,
    phone: str,
) -> auth.User:
    """Update and return given user and its profile w/ data from form"""

    # FIXME existing value are kept instead of new ones, why?

    user.first_name = user.first_name or first_name
    user.last_name = user.last_name or last_name
    user.save()

    organization = get_organization(site, org_name)

    profile = user.profile
    profile.organization = profile.organization or organization
    profile.phone_no = profile.phone_no or phone
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
        template_name=communication_constants.TPL_PROJECT_RECEIVED,
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
        template_name=communication_constants.TPL_SHARING_INVITATION,
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
