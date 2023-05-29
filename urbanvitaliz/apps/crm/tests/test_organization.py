import pytest
from django.contrib.sites import models as site_models
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.home import models as home_models
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.utils import login


########################################################################
# organization list
########################################################################


@pytest.mark.django_db
def test_crm_organization_list_not_available_for_non_staff(client):
    url = reverse("crm-organization-list")
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_organization_list_contains_site_organizations(request, client):
    site = get_current_site(request)

    from_abook = baker.make(addressbook_models.Organization)
    from_abook.sites.add(site)

    from_home = baker.make(addressbook_models.Organization)
    profile = baker.make(auth_models.User).profile
    profile.organization = from_home
    profile.sites.add(site)
    profile.save()

    other = baker.make(addressbook_models.Organization)

    url = reverse("crm-organization-list")

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-organization-details", args=[from_abook.id])
    assertContains(response, expected)
    expected = reverse("crm-organization-details", args=[from_home.id])
    assertContains(response, expected)

    unexpected = reverse("crm-organization-details", args=[other.id])
    assertNotContains(response, unexpected)


@pytest.mark.django_db
def test_crm_organization_list_filters_organizations_by_name(request, client):
    site = get_current_site(request)

    expected = baker.make(addressbook_models.Organization)
    expected.sites.add(site)

    unexpected = baker.make(addressbook_models.Organization)
    unexpected.sites.add(site)

    url = reverse("crm-organization-list") + f"?name={expected.name[5:15]}"

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-organization-details", args=[expected.id])
    assertContains(response, expected)

    unexpected = reverse("crm-organization-details", args=[unexpected.id])
    assertNotContains(response, unexpected)


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


@pytest.mark.django_db
def test_crm_organisation_details_accessible_w_multiple_users(request, client):
    """Introduced following bug in production when multiple profile on organization"""
    site = get_current_site(request)
    o = baker.make(addressbook_models.Organization, sites=[site])

    profile = baker.make(auth_models.User).profile
    profile.organization = o
    profile.sites.add(site)
    profile.save()

    profile = baker.make(auth_models.User).profile
    profile.organization = o
    profile.sites.add(site)
    profile.save()

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
    a = baker.make(addressbook_models.Organization, sites=[site])
    b = baker.make(addressbook_models.Organization, sites=[site])

    url = reverse("crm-organization-merge") + f"?org_ids={a.id}&org_ids={b.id}"

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    assertContains(response, a.name)
    assertContains(response, b.name)


@pytest.mark.django_db
def test_crm_organization_merge_page_with_empty_list(request, client):
    site = get_current_site(request)

    url = reverse("crm-organization-merge")

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    # empty list redirects to list
    assert response.status_code == 302


@pytest.mark.django_db
def test_crm_organization_merge_processing(request, client):
    site = get_current_site(request)

    departments = baker.make(geomatics.Department, _quantity=4)

    orgs = []
    for d in departments:
        o = baker.make(addressbook_models.Organization)
        o.sites.add(site)
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
    assert set(org_dpts) == set(d.code for d in departments)


@pytest.mark.django_db
def test_crm_organization_merge_empty_list(request, client):
    site = get_current_site(request)

    url = reverse("crm-organization-merge")

    data = {"name": "A clean new name", "org_ids": []}

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url, data=data)

    # no failure, just a redirection
    assert response.status_code == 302


# eof
