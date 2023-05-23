import pytest
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker

from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.utils import login


########################################################################
# update organization
########################################################################


@pytest.mark.django_db
def test_crm_organization_update_page_requires_permission(request, client):
    org = baker.make(addressbook_models.Organization)

    url = reverse("crm-organization-update", args=[org.id])

    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_organization_update_page_with_permission(request, client):
    site = get_current_site(request)

    org = baker.make(addressbook_models.Organization)
    org.sites.add(site)

    url = reverse("crm-organization-update", args=[org.id])

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_organization_update_processing(request, client):
    site = get_current_site(request)

    departments = baker.make(geomatics.Department, _quantity=4)

    org = baker.make(addressbook_models.Organization)
    org.sites.add(site)

    url = reverse("crm-organization-update", args=[org.id])

    selected = [d.code for d in departments[1:3]]
    data = {"name": "a new name", "departments": selected}

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url, data=data)

    assert response.status_code == 302

    # org data is updated
    org.refresh_from_db()
    assert org.name == data["name"]
    org_dpts = (d.code for d in org.departments.all())
    assert set(org_dpts) == set(selected)


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


########################################################################
# merge organizations
########################################################################


@pytest.mark.django_db
def test_crm_organization_merge_page_requires_permission(request, client):
    org = baker.make(addressbook_models.Organization)

    url = reverse("crm-organization-merge")

    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_organization_merge_page_with_permission(request, client):
    site = get_current_site(request)

    org = baker.make(addressbook_models.Organization)
    org.sites.add(site)

    url = reverse("crm-organization-merge")

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_organization_merge_processing(request, client):
    site = get_current_site(request)

    departments = baker.make(geomatics.Department, _quantity=4)

    orgs = []
    for d in departments:
        o = baker.make(addressbook_models.Organization)
        o.departments.add(d)
        orgs.append(o)

    url = reverse("crm-organization-merge")

    data = {"name": "A clean new name", "org_ids": [o.id for o in orgs]}

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url, data=data)

    assert response.status_code == 302

    # org data is updated
    orgs = addressbook_models.Organization.objects.all()

    assert len(orgs) == 1

    org = orgs[0]
    assert org.name == data["name"]
    org_dpts = (d.code for d in org.departments.all())
    assert set(org_dpts) == set(d.id for d in departments)


# eof
