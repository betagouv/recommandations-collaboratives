import pytest
from django.contrib.sites.models import Site
from django.urls import reverse
from model_bakery import baker

from ...geomatics.models import Department
from ..models import Contact, Organization, OrganizationGroup


@pytest.fixture
def acme_organization(current_site):
    organization = baker.make(
        Organization, name="acme corporation", sites=[current_site]
    )
    baker.make(Contact, organization=organization)
    return organization


@pytest.mark.django_db
def test_anonymous_can_list_organizations_but_not_create(api_client):
    url = reverse("api-addressbook-organization-list")

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.post(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_can_search_organizations(api_client, acme_organization):
    url = reverse("api-addressbook-organization-list")
    response = api_client.get(url, {"search": "acme"})

    assert response.status_code == 200
    assert len(response.data) > 0


@pytest.mark.django_db
def test_anonymous_can_read_organization_but_not_update(api_client, acme_organization):
    url = reverse("api-addressbook-organization-detail", args=[acme_organization.pk])

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.put(url, data={})
    assert response.status_code == 403

    response = api_client.patch(url, data={})
    assert response.status_code == 403

    response = api_client.delete(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
def test_create(api_client, staff_user):
    group = baker.make(OrganizationGroup)
    baker.make(Department, code="01")
    baker.make(Department, code="32")
    url = reverse("api-addressbook-organization-list")

    api_client.force_authenticate(staff_user)
    response = api_client.post(
        url, {"group_id": group.id, "name": "orga_name", "departments": ["01", "32"]}
    )
    assert response.data["group_id"] == group.id
    assert set(response.data["departments"]) == {"01", "32"}
    assert response.data["name"] == "orga_name"


@pytest.mark.django_db
def test_update(api_client, staff_user, current_site):
    group = baker.make(OrganizationGroup)
    baker.make(Department, code="01")
    baker.make(Department, code="32")
    orga = baker.make(Organization, sites=[current_site])
    url = reverse("api-addressbook-organization-detail", args=[orga.id])

    api_client.force_authenticate(staff_user)
    response = api_client.patch(
        url, {"group_id": group.id, "name": "orga_name", "departments": ["01", "32"]}
    )
    assert response.data["group_id"] == group.id
    assert set(response.data["departments"]) == {"01", "32"}
    assert response.data["name"] == "orga_name"


@pytest.mark.django_db
def test_add_sites_to_orga_when_created_same_name(api_client, staff_user):
    site = baker.make(Site)
    organization = baker.make(Organization, name="Services Secrets 91", sites=[site])
    url = reverse("api-addressbook-organization-list")
    api_client.force_authenticate(staff_user)
    response = api_client.post(url, {"name": organization.name})
    assert response.data["id"] == organization.id
    assert response.status_code == 200
    organization.refresh_from_db()
    assert site in organization.sites.all()
