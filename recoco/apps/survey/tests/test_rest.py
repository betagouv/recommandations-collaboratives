import pytest
from django.urls import reverse

# from django.contrib.sites.shortcuts import get_current_site

# TODO: move to global somewhere
@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.mark.django_db
def test_session_view(request, api_client):
    # site = get_current_site(request)

    response = api_client.get(
        path=reverse("api-survey-sessions"),
    )
    assert response.status_code == 403

    # TODO: add tests
