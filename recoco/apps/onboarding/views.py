# encoding: utf-8

"""
views for onboarding new users/projects

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-17 20:39:35 CEST
"""

import uuid

from allauth.account.views import LoginView
from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites import models as sites
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode

from recoco.apps.addressbook import models as addressbook
from recoco.apps.geomatics import models as geomatics
from recoco.apps.projects import models as projects
from recoco.apps.projects.utils import (
    assign_advisor,
    assign_collaborator,
    generate_ro_key,
    refresh_user_projects_in_session,
)
from recoco.apps.survey import models as survey_models
from recoco.apps.survey.forms import AnswerForm
from recoco.utils import (
    is_switchtender_or_403,
)

from . import forms, models, utils


class OnboardingLogin(LoginView):
    """Allauth login view overriden to match onboarding style"""

    template_name = "onboarding/onboarding-signin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_site = self.request.site

        onboarding_uuid_str: str | None = self.request.session.get(
            "onboarding_uuid", None
        )

        context["user_other_sites"] = []
        if onboarding_uuid_str is not None:
            try:
                project_creation_request = projects.ProjectCreationRequest.objects.get(
                    site=self.request.site, uuid=uuid.UUID(onboarding_uuid_str)
                )
                onboarding_user = auth.User.objects.get(
                    username=project_creation_request.email
                )
                context["onboarding_email"] = onboarding_user.email
                context["user_other_sites"] = onboarding_user.profile.sites.exclude(
                    id=current_site.id
                )
            except projects.ProjectCreationRequest.DoesNotExist:
                pass
            except auth.User.DoesNotExist:
                pass

        return context

    def form_valid(self, form):
        """Process the valid form submission"""
        redirect_url = self.get_success_url()

        try:
            # Get project creation request for this email if it exists
            project_creation_request = (
                projects.ProjectCreationRequest.objects.filter(
                    site=self.request.site, email=form.cleaned_data.get("login")
                )
                .order_by("-created")
                .first()
            )
        except projects.ProjectCreationRequest.DoesNotExist as e:
            raise Http404 from e

        project = project_creation_request.project

        super().form_valid(form)

        # Update project with new user
        project.submitted_by = self.request.user
        project.first_name = self.request.user.first_name
        project.last_name = self.request.user.last_name
        project.org_name = self.request.user.profile.organization.name
        project.phone = self.request.user.profile.phone_no
        project_site = projects.ProjectSite.objects.get(
            project=project, site=self.request.site
        )
        project_site.status = "DRAFT"
        project_site.save()
        project.save()

        # Delete project creation request
        project_creation_request.delete()

        # Assign user as project owner
        assign_collaborator(self.request.user, project, is_owner=True)

        # Send notifications
        utils.notify_new_project(self.request.site, project, self.request.user)
        utils.email_owner_of_project(self.request.site, project, self.request.user)

        refresh_user_projects_in_session(self.request, self.request.user)

        # Override redirect to go to project summary
        redirect_url = reverse("onboarding-summary", args=(project.pk,))

        return redirect(redirect_url)


########################################################################
# User driven onboarding for a new project
########################################################################


def onboarding_signup(request):
    """
    Return the onboarding signup page and process onboarding signup submission.
    We should only be here if we have filled in a Project Creation Request first.
    """
    site_config = request.site_config

    if request.user.is_authenticated:
        return redirect(reverse("onboarding-project"))

    project_request_uuid = request.session.get("onboarding_uuid") or request.GET.get(
        "onboarding_uuid"
    )

    if not project_request_uuid:
        return redirect(reverse("onboarding-project"))

    # Retrieve the project creation request for the uuid
    project_creation_request = (
        projects.ProjectCreationRequest.objects.filter(
            site=request.site, uuid=uuid.UUID(project_request_uuid)
        )
        .order_by("-created")
        .first()
    )

    if not project_creation_request:
        return redirect(reverse("onboarding-project"))

    form = forms.OnboardingSignupForm(
        request.POST or None, initial={"email": project_creation_request.email}
    )

    if request.method == "POST" and form.is_valid():
        user, is_new_user = auth.User.objects.get_or_create(
            username=project_creation_request.email,
            defaults={
                "email": project_creation_request.email,
                "first_name": form.cleaned_data.get("first_name"),
                "last_name": form.cleaned_data.get("last_name"),
            },
        )

        if not is_new_user:
            # user exists but is not currently logged in,
            request.session["onboarding_uuid"] = str(project_creation_request.uuid)

            login_url = reverse("onboarding-signin")
            next_args = urlencode(
                {
                    "next": reverse(
                        "onboarding-summary",
                        args=(project_creation_request.project_id,),
                    )
                }
            )
            return redirect(f"{login_url}?{next_args}")

        user.set_password(form.cleaned_data.get("password"))
        user = update_user(
            site=request.site,
            user=user,
            first_name=form.cleaned_data.get("first_name"),
            last_name=form.cleaned_data.get("last_name"),
            org_name=form.cleaned_data.get("org_name"),
            org_position=form.cleaned_data.get("role"),
            phone=form.cleaned_data.get("phone"),
        )

        log_user(request, user, backend="django.contrib.auth.backends.ModelBackend")

        ##--- Starting this point, we are logged in as the submitter ---##

        try:
            project = projects.Project.objects.get(
                id=project_creation_request.project_id
            )
        except projects.Project.objects.DoesNotExist:
            return redirect(reverse("onboarding-project"))

        # Create project from Project Creation Request
        with transaction.atomic():
            project.submitted_by = user
            project_site = projects.ProjectSite.objects.get(
                project=project, site=request.site
            )
            project_site.status = "DRAFT"
            project_site.save()
            project.save()

            # Delete project creation request
            project_creation_request.delete()

            assign_collaborator(user, project, is_owner=True)

            utils.notify_new_project(request.site, project, user)
            utils.email_owner_of_project(request.site, project, user)

            refresh_user_projects_in_session(request, user)

            # Cleanup session
            if "onboarding_uuid" in request.session:
                del request.session["onboarding_uuid"]

            if "project_id" in request.session:
                del request.session["project_id"]

            return redirect(f"{reverse('onboarding-summary', args=(project.id,))}")

    context = {"form": form, "site_config": site_config}
    return render(request, "onboarding/onboarding-signup.html", context)


def onboarding_project(request):
    """Return the onboarding page and process onboarding submission"""
    site_config = request.site_config

    form = forms.OnboardingProject(request.POST or None)

    question_forms = []
    for question in site_config.onboarding_questions.all():
        form_prefix = f"q{question.id}"
        question_forms.append(
            AnswerForm(
                question,
                None,
                request.POST or None,
                prefix=form_prefix,
            )
        )

    if request.user.is_authenticated:
        form.fields["email"].initial = request.user.email
        form.fields["email"].disabled = True

    if request.method == "POST":
        all_forms_valid = form.is_valid()

        for question_form in question_forms:
            all_forms_valid = all_forms_valid and question_form.is_valid()

        if all_forms_valid:
            connected_user = request.user.is_authenticated
            user = request.user if connected_user else None
            project_status = "DRAFT" if connected_user else "PRE_DRAFT"

            project = create_project_for_user(
                site=request.site,
                user=user,
                data=form.cleaned_data,
                status=project_status,
            )

            request.session["project_id"] = project.id

            # Save survey questions
            if site_config.project_survey:
                session, _ = survey_models.Session.objects.get_or_create(
                    project=project, survey=site_config.project_survey
                )

                for question_form in question_forms:
                    question_form.update_session(session, user)

            if connected_user:
                assign_collaborator(user, project, is_owner=True)

                utils.notify_new_project(request.site, project, user)
                utils.email_owner_of_project(request.site, project, user)

                refresh_user_projects_in_session(request, user)

                return redirect(f"{reverse('onboarding-summary', args=(project.pk,))}")
            else:
                project_creation_request = (
                    projects.ProjectCreationRequest.objects.create(
                        site=request.site,
                        email=form.cleaned_data["email"],
                        project=project,
                    )
                )
                project_creation_request.save()
                request.session["onboarding_uuid"] = str(project_creation_request.uuid)

                try:
                    auth.User.objects.get(username=form.cleaned_data["email"])
                    next_args = urlencode(
                        {"next": reverse("onboarding-summary", args=(project.pk,))}
                    )
                    login_url = reverse("onboarding-signin")
                    return redirect(f"{login_url}?{next_args}")
                except auth.User.DoesNotExist:
                    signup_url = reverse("onboarding-signup")
                    return redirect(signup_url)
    context = {
        "form": form,
        "question_forms": question_forms,
        "site_config": site_config,
    }
    return render(request, "onboarding/onboarding-project.html", context)


@login_required
def onboarding_summary(request, project_id=None):
    """Resume project from onboarding"""
    site_config = request.site_config

    project = get_object_or_404(projects.Project, sites=request.site, pk=project_id)

    if not project.location:
        next_url = f"{reverse('survey-project-session' if site_config.project_survey else 'projects-project-detail', args=(project.pk,))}"
    else:
        next_args_for_project_location = urlencode(
            {
                "next": reverse(
                    (
                        "survey-project-session"
                        if site_config.project_survey
                        else "projects-project-detail"
                    ),
                    args=(project.pk,),
                )
            }
        )
        next_url = f"{reverse('projects-project-location', args=(project.pk,))}?{next_args_for_project_location}"

    context = {"project": project, "next_url": next_url, "site_config": site_config}

    return render(request, "onboarding/onboarding-summary.html", context)


########################################################################
# Advisor onboard someone else
########################################################################


def prefill_project_set_user(request):
    """Create a new project for someone else - step 1 create user"""
    site_config = request.site_config

    is_switchtender_or_403(request.user)

    prefill_set_user_data = request.session.get("prefill_set_user")

    form = forms.PrefillSetuserForm(request.POST or None, initial=prefill_set_user_data)

    if request.method == "POST" and form.is_valid():
        request.session["prefill_set_user"] = form.cleaned_data

        return redirect(reverse("onboarding-prefill"))

    return render(request, "onboarding/prefill-user.html", locals())


def prefill_project_submit(request):
    """Create a new project for someone else - step 2 create project"""
    site_config = request.site_config

    is_switchtender_or_403(request.user)

    prefill_set_user_data = request.session.get("prefill_set_user")

    if not prefill_set_user_data:
        return redirect(reverse("onboarding-prefill-set-user"))

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
            # User creation
            email = prefill_set_user_data.get("email").lower()

            user, is_new_user = auth.User.objects.get_or_create(
                username=email, defaults={"email": email}
            )

            if is_new_user:
                user = update_user(
                    site=request.site,
                    user=user,
                    first_name=prefill_set_user_data.get("first_name"),
                    last_name=prefill_set_user_data.get("last_name"),
                    org_name=prefill_set_user_data.get("org_name"),
                    org_position=prefill_set_user_data.get("role"),
                    phone=prefill_set_user_data.get("phone"),
                )

            # Project creation
            project = create_project_for_user(
                site=request.site,
                user=user,
                submitted_by=request.user,
                data=form.cleaned_data,
                status="TO_PROCESS",
            )

            project.sites.add(request.site)

            # Save survey questions
            if site_config.project_survey:
                session, _ = survey_models.Session.objects.get_or_create(
                    project=project, survey=site_config.project_survey
                )

                for question_form in question_forms:
                    question_form.update_session(session, request.user)

            assign_collaborator(user, project, is_owner=True)
            assign_advisor(request.user, project, request.site)

            utils.invite_user_to_project(
                request=request,
                user=user,
                project=project,
                message=prefill_set_user_data.get("message"),
            )
            utils.notify_new_project(request.site, project, user)

            # cleanup now useless prefill existing data if present
            if "prefill_set_user" in request.session:
                del request.session["prefill_set_user"]

            return redirect(
                reverse("projects-project-detail-overview", args=(project.pk,))
            )

    return render(request, "onboarding/prefill-project.html", locals())


@transaction.atomic
def create_project_for_user(
    site, user: auth.User, data: dict, status: str, submitted_by: auth.User = None
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
        ro_key=generate_ro_key(),
    )

    project.project_sites.create(site=site, status=status, is_origin=True)

    return project


def update_user(
    site: sites.Site,
    user: auth.User,
    first_name: str,
    last_name: str,
    org_name: str,
    org_position: str,
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
    profile.organization_position = org_position or None
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
        content=(f"# Demande initiale\n\n{project.description}\n\n{markdown_content}"),
        public=True,
        site=site,
    )


# eof
