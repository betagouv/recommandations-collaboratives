from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from urbanvitaliz.apps.addressbook.models import Organization
from urbanvitaliz.apps.projects.models import Project


def organization_details(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)

    participants = User.objects.filter(
        profile__in=organization.registered_profiles.all()
    )

    advised_projects = Project.objects.filter(switchtenders__in=participants)
    unadvised_projects = Project.objects.exclude(switchtenders__in=participants)

    return render(request, "crm/organization_details.html", locals())


def user_details(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    return render(request, "crm/user_details.html", locals())


def project_details(request, project_id):
    user = get_object_or_404(Project, pk=project_id)

    return render(request, "crm/project_details.html", locals())
