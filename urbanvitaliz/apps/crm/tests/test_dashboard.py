import pytest
from actstream import action
from django.conf import settings
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains

from urbanvitaliz.apps.projects import models as project_models
from urbanvitaliz.utils import login


@pytest.mark.django_db
def test_site_dashboard_not_available_for_non_staff_users(client):
    url = reverse("crm-site-dashboard")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_site_dashboard_available_for_staff_users(request, client):
    site = get_current_site(request)
    project = baker.make(project_models.Project, sites=[site])
    action.send(project, verb="Was here", target=project)

    other = baker.make(site_models.Site)
    with settings.SITE_ID.override(other.pk):
        other = baker.make(project_models.Project, sites=[other])
        action.send(other, verb="Was not here", target=other)

    url = reverse("crm-site-dashboard")
    with login(client, groups=["example_com_staff"]) as user:
        response = client.get(url)

    assert response.status_code == 200

    assertContains(response, "Was here")
    assertNotContains(response, "Was not here")


# eof
