import collections

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import assign_perm
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import get_group_for_site, login

from .. import models, views


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
