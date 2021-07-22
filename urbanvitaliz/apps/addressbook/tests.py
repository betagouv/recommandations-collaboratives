import pytest
from pytest_django.asserts import assertContains

from model_bakery.recipe import Recipe

from django.urls import reverse

from urbanvitaliz.utils import login

from . import models


########################################################################################
# Organization
########################################################################################

# Creation


@pytest.mark.django_db
def test_create_organization_not_available_for_non_staff_users(client):
    Recipe(models.Organization).make()
    url = reverse("addressbook-organization-create")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_organization_available_for_staff_users(client):
    Recipe(models.Organization).make()
    url = reverse("addressbook-organization-create")
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-organization-create"')


# Listing


@pytest.mark.django_db
def test_organization_list_not_available_for_non_staff_users(client):
    url = reverse("addressbook-organization-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_organization_list_available_for_staff_users(client):
    url = reverse("addressbook-organization-list")
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200


########################################################################################
# Contact
########################################################################################

# Creation


@pytest.mark.django_db
def test_create_contact_not_available_for_non_staff_users(client):
    organization = Recipe(models.Organization).make()
    url = reverse(
        "addressbook-organization-contact-create",
        args=[organization.id],
    )
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_contact_available_for_staff_users(client):
    organization = Recipe(models.Organization).make()
    url = reverse(
        "addressbook-organization-contact-create",
        args=[organization.id],
    )
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-contact-create"')
