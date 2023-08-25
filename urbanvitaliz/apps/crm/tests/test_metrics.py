import pytest
from django.urls import reverse

from urbanvitaliz.utils import login


@pytest.mark.django_db
def test_reco_without_resources_not_available_for_non_crm_users(client):
    url = reverse("crm-reco-without-resources")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_reco_without_resources_available_to_crm_user(request, client):
    url = reverse("crm-reco-without-resources")

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
