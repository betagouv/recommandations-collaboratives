import pytest
from django.urls import reverse
from model_bakery import baker

from ..models import Contact, Organization


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
