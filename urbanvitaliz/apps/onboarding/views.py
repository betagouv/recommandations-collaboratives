from django.contrib.auth import login as log_user
from django.contrib.auth import models as auth
from django.shortcuts import redirect, render, reverse
from django.views.generic.edit import CreateView
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
    form = forms.OnboardingResponseForm(request.POST or None)
    onboarding_instance = models.Onboarding.objects.get(pk=site_config.onboarding.pk)
    # Add fields in JSON to dynamic form rendering field.
    form.fields["response"].add_fields(onboarding_instance.form)

    if request.method == "POST":
        if form.is_valid():
            onboarding_response = form.save(commit=False)
            onboarding_response.onboarding = onboarding_instance
            onboarding_response.save()

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

            project.save()
            project.sites.add(request.site)

            user, _ = auth.User.objects.get_or_create(
                username=form.cleaned_data.get("email"),
                defaults={
                    "email": form.cleaned_data.get("email"),
                    "first_name": form.cleaned_data.get("first_name"),
                    "last_name": form.cleaned_data.get("last_name"),
                },
            )

            # Make her project owner
            projects.ProjectMember.objects.create(
                member=user, project=project, is_owner=True
            )

            log_user(request, user, backend="django.contrib.auth.backends.ModelBackend")

            # Create initial public note
            # XXX update so optinal fields are written into a note
            projects.Note(
                project=project,
                content=f"# Demande initiale\n\n{project.impediments}",
                public=True,
            ).save()

            # All green, notify
            projects_signals.project_submitted.send(
                sender=projects.Project, submitter=user, project=project
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

            response = redirect("survey-project-session", project_id=project.id)
            response["Location"] += "?first_time=1"
            return response

    return render(request, "onboarding/onboarding.html", locals())
