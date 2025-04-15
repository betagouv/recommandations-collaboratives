# encoding: utf-8

"""
Tests for project application

authors: guillaume.libersat@beta.gouv.fr
created: 2024-07-29 09:19:52 CEST
"""

import pytest
from django.urls import reverse

from recoco.utils import login


@pytest.mark.django_db
def test_project_map_not_accessible_when_not_logged_in(request, client):
    url = reverse("projects-project-list-map")
    response = client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_project_map_not_accessible_for_collectivity(request, client):
    url = reverse("projects-project-list-map")

    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_map_accessible_for_advisors(request, client):
    url = reverse("projects-project-list-map")

    with login(client, groups=["example_com_advisor"]):
        response = client.get(url)

    assert response.status_code == 200
