import pytest
from django.urls import reverse

from urbanvitaliz.utils import login


@pytest.mark.django_db
def test_site_dashboard_not_available_for_non_staff_users(client):
    url = reverse("crm-site-dashboard")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_site_dashboard_available_for_staff_users(client):
    url = reverse("crm-site-dashboard")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200


# eof
