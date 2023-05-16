import pytest
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker

from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.utils import login

########################################################################
# details
########################################################################


@pytest.mark.django_db
def test_crm_organisation_details_not_accessible_wo_perm(request, client):
    site = get_current_site(request)
    o = baker.make(addressbook_models.Organization, sites=[site])

    url = reverse("crm-organization-details", args=[o.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_organisation_details_not_accessible_other_site(request, client):
    site = get_current_site(request)
    other = baker.make(site_models.Site)
    o = baker.make(addressbook_models.Organization, sites=[other])

    url = reverse("crm-organization-details", args=[o.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_organisation_details_accessible_w_perm(request, client):
    site = get_current_site(request)
    o = baker.make(addressbook_models.Organization, sites=[site])

    url = reverse("crm-organization-details", args=[o.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


# eof
