# encoding: utf-8

"""
Tests for resources rest API

authors: sebastien.reuiller@beta.gouv.fr
created: 2024-02-05 17:11:56 CEST
"""

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery.recipe import Recipe, baker
from rest_framework.test import APIClient

from .. import models

########################################################################
# list of resources
########################################################################


@pytest.mark.django_db
def test_anonymous_can_see_resources_list_api(request):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()

    url = reverse("resources-list")
    client = APIClient()
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 1

    first = response.data["results"][0]
    assert first["title"] == resource.title


@pytest.mark.django_db
def test_anonymous_cannot_see_unpublished_resource_in_list_api(request):
    Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.TO_REVIEW,
        title=" to review resource",
    ).make()

    client = APIClient()
    response = client.get(reverse("resources-list"))

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_staff_can_see_unpublished_resource_in_list_api(request):
    site = get_current_site(request)
    resource = Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.TO_REVIEW,
        title=" to review resource",
    ).make()

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.get(reverse("resources-list"))

    assert response.status_code == 200
    assert response.data["count"] == 1

    first = response.data["results"][0]
    assert first["title"] == resource.title


@pytest.mark.django_db
def test_simple_user_cannot_create_resource_with_api(request):
    site = get_current_site(request)

    user = baker.make(auth_models.User)
    user.profile.sites.add(site)

    url = reverse("resources-list")
    client = APIClient()
    client.force_authenticate(user=user)

    data = {
        "title": "one resource",
        "subtitle": "one resource to test",
        "status": 1,
        "tags": ["a tag"],
    }
    response = client.post(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_user_can_create_resource_with_api(request):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    url = reverse("resources-list")
    client = APIClient()
    client.force_authenticate(user=staff)

    data = {
        "title": "one resource",
        "subtitle": "one resource to test",
        "status": 1,
        "tags": ["a tag"],
    }
    response = client.post(url, data=data)

    assert response.status_code == 201
    assert response.data["title"] == data["title"]
    assert response.data["created_by"]["first_name"] == staff.first_name
    assert response.data["created_by"]["last_name"] == staff.last_name
