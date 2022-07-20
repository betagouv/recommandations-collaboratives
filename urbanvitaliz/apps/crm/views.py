"""
Urls for crm application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-07-20 12:27:25 CEST
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from urbanvitaliz.apps.addressbook.models import Organization
from urbanvitaliz.apps.projects.models import Project


@staff_member_required
def organization_details(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)

    participants = User.objects.filter(
        profile__in=organization.registered_profiles.all()
    )

    advised_projects = Project.objects.filter(switchtenders__in=participants)

    org_departments = organization.departments.all()

    unadvised_projects = Project.objects.filter(
        commune__department__in=org_departments
    ).exclude(switchtenders__in=participants)

    return render(request, "crm/organization_details.html", locals())


@staff_member_required
def user_details(request, user_id):
    crm_user = get_object_or_404(User, pk=user_id)

    return render(request, "crm/user_details.html", locals())


@staff_member_required
def project_details(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    return render(request, "crm/project_details.html", locals())
