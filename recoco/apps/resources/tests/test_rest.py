# encoding: utf-8

"""
Tests for resources rest API

authors: sebastien.reuiller@beta.gouv.fr
created: 2024-02-05 17:11:56 CEST
"""

import json

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery.recipe import Recipe, baker

from .. import models

########################################################################
# list of resources
########################################################################


@pytest.mark.django_db
def test_anonymous_can_see_resources_list_api(request, api_client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["results"][0]["title"] == resource.title


@pytest.mark.django_db
def test_resources_list_does_not_include_content(request, api_client):
    Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url)
    assert response.status_code == 200

    assert "content" not in response.data["results"][0]


@pytest.mark.django_db
def test_resource_details_includes_content(request, api_client):
    resource = Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.PUBLISHED,
        title=" public resource",
    ).make()

    url = reverse("resources-detail", args=(resource.pk,))
    response = api_client.get(url)
    assert response.status_code == 200

    assert "content" in response.data


@pytest.mark.django_db
def test_anonymous_cannot_see_unpublished_resource_in_list_api(request, api_client):
    Recipe(
        models.Resource,
        sites=[get_current_site(request)],
        status=models.Resource.TO_REVIEW,
        title=" to review resource",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_staff_can_see_unpublished_resource_in_list_api(request, api_client):
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

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == resource.title


@pytest.mark.django_db
def test_simple_user_cannot_create_resource_with_api(request, api_client):
    site = get_current_site(request)

    user = baker.make(auth_models.User)
    user.profile.sites.add(site)

    url = reverse("resources-list")
    api_client.force_authenticate(user=user)

    data = {
        "title": "one resource",
        "subtitle": "one resource to test",
        "status": 1,
        "tags": ["a tag"],
    }
    response = api_client.post(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_user_can_create_resource_with_api(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_advisor")
    staff.groups.add(gstaff)

    category = baker.make(models.Category)

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)

    data = {
        "title": "one resource",
        "subtitle": "one resource to test",
        "status": 1,
        "tags": ["a tag"],
        "content": "toto",
        "category": category.id,
    }
    response = api_client.post(url, data=data)

    assert response.status_code == 201
    assert response.data["title"] == data["title"]
    assert response.data["created_by"]["first_name"] == staff.first_name
    assert response.data["created_by"]["last_name"] == staff.last_name


@pytest.mark.django_db
def test_staff_user_can_edit_resource_with_api(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_advisor")
    staff.groups.add(gstaff)
    other_user = baker.make(auth_models.User)

    resource = baker.make(
        models.Resource,
        title="titre",
        content="blabla",
        sites=[site],
        created_by=other_user,
    )
    category = baker.make(models.Category)

    url = reverse("resources-detail", args=[resource.pk])
    api_client.force_authenticate(user=staff)

    data = {
        "title": "one resource",
        "subtitle": "one resource to test",
        "status": 1,
        "tags": ["a tag"],
        "content": "toto",
        "category": category.id,
    }
    response = api_client.put(url, data=data)

    assert response.status_code == 200
    assert response.data["title"] == data["title"]
    assert response.data["created_by"]["first_name"] == resource.created_by.first_name
    assert response.data["created_by"]["last_name"] == resource.created_by.last_name


########################################################################
# filters and search
########################################################################


@pytest.mark.django_db
def test_filter_resources_by_category(request, api_client):
    site = get_current_site(request)
    cat_a = baker.make(models.Category, sites=[site])
    cat_b = baker.make(models.Category, sites=[site])

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat_a,
        title="Resource A",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat_b,
        title="Resource B",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url, {"category": cat_a.pk})
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Resource A"


@pytest.mark.django_db
def test_filter_resources_by_single_status(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.DRAFT,
        title="Draft resource",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        title="Published resource",
    ).make()

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)
    response = api_client.get(url, {"status": models.Resource.DRAFT})
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Draft resource"


@pytest.mark.django_db
def test_filter_resources_by_multiple_statuses(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.DRAFT,
        title="Draft resource",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.TO_REVIEW,
        title="To review resource",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        title="Published resource",
    ).make()

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)
    response = api_client.get(
        url, {"status": [models.Resource.DRAFT, models.Resource.TO_REVIEW]}
    )
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 2
    titles = {r["title"] for r in results}
    assert titles == {"Draft resource", "To review resource"}


@pytest.mark.django_db
def test_filter_resources_combined_category_and_status(request, api_client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    cat = baker.make(models.Category, sites=[site])

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat,
        title="Published in category",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.DRAFT,
        category=cat,
        title="Draft in category",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=None,
        title="Published no category",
    ).make()

    url = reverse("resources-list")
    api_client.force_authenticate(user=staff)
    response = api_client.get(
        url, {"category": cat.pk, "status": models.Resource.PUBLISHED}
    )
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Published in category"


@pytest.mark.django_db
def test_search_resources_with_watson(request, api_client):
    site = get_current_site(request)

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        title="Urbanisme durable",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        title="Mobilité douce",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url, {"search": "urbanisme"})
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Urbanisme durable"


@pytest.mark.django_db
def test_search_resources_combined_with_filters(request, api_client):
    site = get_current_site(request)
    cat = baker.make(models.Category, sites=[site])

    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=cat,
        title="Urbanisme durable",
    ).make()
    Recipe(
        models.Resource,
        sites=[site],
        status=models.Resource.PUBLISHED,
        category=None,
        title="Urbanisme ancien",
    ).make()

    url = reverse("resources-list")
    response = api_client.get(url, {"search": "urbanisme", "category": cat.pk})
    assert response.status_code == 200
    results = response.data["results"]
    assert len(results) == 1
    assert results[0]["title"] == "Urbanisme durable"


class TestRessourceAddonViewSet:
    @pytest.mark.django_db
    def test_not_authenticated(self, api_client):
        response = api_client.get(reverse("resource-addons-list"))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_not_authorized(self, api_client):
        user = baker.make(auth_models.User)
        api_client.force_authenticate(user)
        response = api_client.get(reverse("resource-addons-list"))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_list_resource_addons(self, api_client, current_site):
        user = baker.make(auth_models.User)
        assign_perm("sites.manage_resources", user, current_site)

        resource_addon = baker.make(
            models.ResourceAddon,
            nature="hub_with_iframe",
            recommendation__site=current_site,
            data={
                "title": "Hub avec iframe",
                "iframe_url": "https://www.example.com",
            },
            enabled=True,
        )

        api_client.force_authenticate(user)
        response = api_client.get(reverse("resource-addons-list"))
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0] == {
            "id": resource_addon.id,
            "nature": "hub_with_iframe",
            "recommendation": resource_addon.recommendation_id,
            "data": {
                "title": "Hub avec iframe",
                "iframe_url": "https://www.example.com",
            },
            "enabled": True,
        }

    @pytest.mark.django_db
    def test_create_resource_addon(self, api_client, current_site):
        user = baker.make(auth_models.User)
        assign_perm("sites.manage_resources", user, current_site)

        resource = baker.make("resources.Resource", sites=[current_site])
        recommendation = baker.make("tasks.Task", site=current_site, resource=resource)

        api_client.force_authenticate(user)
        response = api_client.post(
            reverse("resource-addons-list"),
            data={
                "nature": "hub_with_iframe",
                "recommendation": recommendation.id,
                "data": json.dumps(
                    {
                        "title": "Hub avec iframe",
                        "iframe_url": "https://www.example.com",
                    }
                ),
                "enabled": True,
            },
        )
        assert response.status_code == 201

        recommendation.refresh_from_db()

        assert recommendation.resource_addons.count() == 1
        addon = recommendation.resource_addons.first()
        assert addon.nature == "hub_with_iframe"
        assert addon.recommendation == recommendation
        assert addon.data == {
            "title": "Hub avec iframe",
            "iframe_url": "https://www.example.com",
        }
        assert addon.enabled is True
