from django.shortcuts import get_object_or_404, render
from urbanvitaliz.apps.addressbook.models import Organization


def organization_details(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)

    return render(request, "crm/organization_details.html", locals())
