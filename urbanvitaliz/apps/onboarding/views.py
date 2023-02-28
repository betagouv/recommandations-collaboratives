from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.db.models import Q
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
from urbanvitaliz.apps.projects.utils import generate_ro_key
from urbanvitaliz.utils import get_site_config_or_503

from . import forms, models


def onboarding(request):
    """Return the onboarding page"""
    site_config = get_site_config_or_503(request.site)

    # Fetch the onboarding form associated with the current site
    form = forms.OnboardingResponseWithCaptchaForm(request.POST or None)
    onboarding_instance = models.Onboarding.objects.get(pk=site_config.onboarding.pk)
    # Add fields in JSON to dynamic form rendering field.
    form.fields["response"].add_fields(onboarding_instance.form)

    if request.method == "POST":
        if form.is_valid():
            onboarding_response = form.save(commit=False)
            onboarding_response.onboarding = onboarding_instance

            project = projects.Project()

            project.name = form.cleaned_data.get("name")
            project.phone = form.cleaned_data.get("phone")
            project.org_name = form.cleaned_data.get("org_name")
            project.description = form.cleaned_data.get("description")
            project.location = form.cleaned_data.get("location")
            project.postcode = form.cleaned_data.get("postcode")

            project.ro_key = generate_ro_key()
            insee = form.cleaned_data.get("insee", None)
            if insee:
                project.commune = geomatics.Commune.get_by_insee_code(insee)
            else:
                postcode = form.cleaned_data.get("postcode")
                project.commune = geomatics.Commune.get_by_postal_code(postcode)

            email = form.cleaned_data.get("email").lower()
            created = False  # for future redirection at end of view

            if request.user.is_authenticated:
                user = request.user
            else:
                user_exists = auth.User.objects.filter(
                    Q(email=email) | Q(username=email)
                ).count()
                if user_exists:  # ask for authentication
                    # TODO store data into session (json?) for when coming back
                    login_url = reverse("account_login")
                    next_args = urlencode({"next": reverse("projects-onboarding")})
                    return redirect(f"{login_url}?{next_args}")
                else:  # create new user
                    user = auth.User.objects.create(username=email, email=email)
                    created = True

            # Update user profile if blank
            user.first_name = user.first_name or form.cleaned_data.get("first_name")
            user.last_name = user.last_name or form.cleaned_data.get("last_name")
            user.save()
            profile = user.profile
            org_name = form.cleaned_data.get("org_name")
            if org_name:
                org, _ = addressbook_models.Organization.objects.get_or_create(
                    name=org_name
                )
                profile.organization = profile.organization or org

            profile.phone_no = profile.phone_no or form.cleaned_data.get("phone")
            profile.save()

            project.submitted_by = user

            # save project
            project.save()
            project.sites.add(request.site)

            # Save onboarding
            onboarding_response.project = project
            onboarding_response.save()

            # Make her project owner
            projects.ProjectMember.objects.create(
                member=user, project=project, is_owner=True
            )

            log_user(request, user, backend="django.contrib.auth.backends.ModelBackend")

            markdown_content = render_to_string(
                "projects/project/onboarding_initial_note.md",
                {
                    "onboarding_response": onboarding_response,
                    "project": project,
                },
            )

            # Create initial note
            projects.Note(
                project=project,
                content=f"# Demande initiale\n\n{project.description}\n\n{ markdown_content }",
                public=True,
            ).save()

            # All green, notify
            projects_signals.project_submitted.send(
                sender=projects.Project,
                site=request.site,
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

            # NOTE check if commune is unique for code postal
            if not insee and project.commune:
                communes = geomatics.Commune.objects.filter(
                    postal=project.commune.postal
                )
                if communes.count() > 1:
                    url = reverse(
                        "projects-onboarding-select-commune", args=[project.id]
                    )
                    return redirect(url)

            if created:
                next_url = (
                    reverse("survey-project-session", args=(project.id,))
                    + "?first_time=1"
                )
                next_args = urlencode({"next": next_url})
                return redirect(f"{reverse('home-user-setup-password')}?{next_args}")
            else:
                response = redirect("survey-project-session", project_id=project.id)
                response["Location"] += "?first_time=1"
                return response

    return render(request, "onboarding/onboarding.html", locals())
