import pytest
from django.urls import reverse
from model_bakery import baker

from recoco.utils import login

from ..models import OrganizationGroup


@pytest.mark.django_db
def test_anonymous_cannot_list_organizationgroups_nor_create(api_client):
    url = reverse("api-addressbook-organization-group-list")

    response = api_client.get(url)
    assert response.status_code == 403

    response = api_client.post(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_in_user_cannot_list_organizationgroups_nor_create(api_client):
    url = reverse("api-addressbook-organization-group-list")

    with login(api_client):
        response = api_client.get(url)
        assert response.status_code == 403

        response = api_client.post(url, data={})
        assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_cannot_read_organizationgroup_nor_update(api_client):
    group = baker.make(OrganizationGroup)

    url = reverse("api-addressbook-organization-group-detail", args=[group.pk])

    response = api_client.get(url)
    assert response.status_code == 403

    response = api_client.put(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_in_user_can_read_organizationgroup_but_not_update(api_client):
    group = baker.make(OrganizationGroup)

    url = reverse("api-addressbook-organization-group-detail", args=[group.pk])

    with login(api_client):
        response = api_client.get(url)
        assert response.status_code == 200

        response = api_client.put(url, data={})
        assert response.status_code == 403


@pytest.mark.django_db
def test_orga_group_search(api_client):
    baker.make(OrganizationGroup, name="ademe")
    z_org = baker.make(OrganizationGroup, name="zoologie")
    search = "zoo"

    with login(api_client, groups=["example_com_staff"]):
        url = reverse("api-addressbook-organization-group-list")
        response = api_client.get(url, {"search": search})
        ids = [search_response["id"] for search_response in response.data["results"]]
        assert ids == [z_org.id]
