import pytest
from django.urls import reverse
from model_bakery import baker

from ..models import OrganizationGroup


@pytest.mark.django_db
def test_anonymous_can_list_organizationgroups_but_not_create(api_client):
    url = reverse("api-addressbook-organization-group-list")

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.post(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_can_read_organizationgroup_but_not_update(api_client):
    group = baker.make(OrganizationGroup)

    url = reverse("api-addressbook-organization-group-detail", args=[group.pk])

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.put(url, data={})
    assert response.status_code == 403
