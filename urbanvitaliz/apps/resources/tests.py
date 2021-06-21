# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-16 17:56:10 CEST
"""

from contextlib import contextmanager

import pytest

from pytest_django.asserts import assertContains
from pytest_django.asserts import assertNotContains
from pytest_django.asserts import assertRedirects

from django.urls import reverse

from django.contrib.auth import models as auth

from model_bakery.recipe import Recipe

from . import models


########################################################################
# resources
########################################################################

#
# search / list


@pytest.mark.django_db
def test_resource_list_not_available_for_non_logged_users(client):
    url = reverse("resources-resource-search")
    response = client.get(url)
    login_url = "{}?next={}".format(reverse("magicauth-login"), url)
    assertRedirects(response, login_url)


@pytest.mark.django_db
def test_resource_list_available_for_logged_users(client):
    url = reverse("resources-resource-search")
    with login(client):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.xfail
@pytest.mark.django_db
def test_resource_list_contains_resource_title_and_link(client):
    resource = Recipe(models.Resource).make()
    url = reverse("resources-resource-search")
    with login(client):
        response = client.get(url)
    assertContains(response, resource.title)
    detail_url = reverse("resources-resource-detail", args=[resource.id])
    assertContains(response, detail_url)


#
# details


@pytest.mark.django_db
def test_resource_detail_not_available_for_non_logged_users(client):
    resource = Recipe(models.Resource).make()
    url = reverse("resources-resource-detail", args=[resource.id])
    response = client.get(url)
    login_url = "{}?next={}".format(reverse("magicauth-login"), url)
    assertRedirects(response, login_url)


@pytest.mark.django_db
def test_resource_detail_available_for_logged_users(client):
    resource = Recipe(models.Resource).make()
    url = reverse("resources-resource-detail", args=[resource.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.xfail
@pytest.mark.django_db
def test_resource_detail_contains_informations(client):
    resource = Recipe(models.Resource).make()
    url = reverse("resources-resource-detail", args=[resource.id])
    with login(client):
        response = client.get(url)
    assertContains(response, resource.title)


@pytest.mark.xfail
@pytest.mark.django_db
def test_resource_detail_contains_update_for_staff(client):
    resource = Recipe(models.Resource).make()
    url = reverse("resources-resource-detail", args=[resource.id])
    with login(client, is_staff=True):
        response = client.get(url)
    update_url = reverse("resources-resource-update", args=[resource.id])
    assertContains(response, update_url)


@pytest.mark.django_db
def test_resource_detail_does_not_contain_update_for_non_staff(client):
    resource = Recipe(models.Resource).make()
    url = reverse("resources-resource-detail", args=[resource.id])
    with login(client):
        response = client.get(url)
    update_url = reverse("resources-resource-update", args=[resource.id])
    assertNotContains(response, update_url)


#
# create


@pytest.mark.django_db
def test_create_resource_not_available_for_non_staff_users(client):
    url = reverse("resources-resource-create")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.xfail
@pytest.mark.django_db
def test_create_resource_available_for_staff_users(client):
    url = reverse("resources-resource-create")
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-resource-create"')


@pytest.mark.django_db
def test_create_new_resource_and_redirect(client):
    data = {"title": "a title", "content": "this is some content"}
    with login(client, is_staff=True):
        response = client.post(reverse("resources-resource-create"), data=data)
    resource = models.Resource.fetch()[0]
    assert resource.content == data["content"]
    assert response.status_code == 302


#
# update


@pytest.mark.django_db
def test_update_resource_not_available_for_non_staff_users(client):
    resource = Recipe(models.Resource).make()
    url = reverse("resources-resource-update", args=[resource.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.xfail
@pytest.mark.django_db
def test_update_resource_available_for_staff_users(client):
    resource = Recipe(models.Resource).make()
    url = reverse("resources-resource-update", args=[resource.id])
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-resource-update"')


@pytest.mark.django_db
def test_update_resource_and_redirect(client):
    resource = Recipe(models.Resource).make()
    url = reverse("resources-resource-update", args=[resource.id])
    data = {"title": "a title", "content": "this is some content"}

    with login(client, is_staff=True):
        response = client.post(url, data=data)

    resource = models.Resource.objects.get(id=resource.id)
    assert resource.content == data["content"]
    assert response.status_code == 302


########################################################################
# Resource searching
########################################################################


@pytest.mark.django_db
def test_search_resources_do_not_match_query():
    resource = Recipe(models.Resource).make()
    unmatched = models.Resource.search(query="notfound")
    assert resource not in unmatched


@pytest.mark.django_db
def test_search_resources_by_tag():
    resource = Recipe(models.Resource, tags="atag").make()
    matched = models.Resource.search(query="tag")
    assert resource in matched


@pytest.mark.django_db
def test_search_resources_by_quote():
    resource = Recipe(models.Resource, quote="a quote").make()
    matched = models.Resource.search(query="quot")
    assert resource in matched


@pytest.mark.django_db
def test_search_resources_by_title():
    resource = Recipe(models.Resource, title="a title").make()
    matched = models.Resource.search(query="titl")
    assert resource in matched


@pytest.mark.django_db
def test_search_resources_by_content():
    resource = Recipe(models.Resource, content="some content...").make()
    matched = models.Resource.search(query="cont")
    assert resource in matched


@pytest.mark.django_db
def test_search_resources_by_category():
    # categories are search like: any category that fits
    categories = [
        Recipe(models.Category).make(),
        Recipe(models.Category).make(),
    ]
    resources = [
        Recipe(models.Resource, category=category).make()
        for category in categories
    ]
    matched = models.Resource.search(categories=categories)
    assert set(resources) == set(matched)


########################################################################
# Helpers
########################################################################


# FIXME duplicated from projects
@contextmanager
def login(client, is_staff=False):
    """Create a user and sign her into the application"""
    user = Recipe(auth.User, email="a@example.com", is_staff=is_staff).make()
    client.force_login(user)
    yield user
