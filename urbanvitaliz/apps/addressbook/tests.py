import pytest

from pytest_django.asserts import assertContains
from pytest_django.asserts import assertRedirects

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


@pytest.mark.django_db
def test_organization_update_and_redirect(client):
    organization = Recipe(models.Organization).make()
    url = reverse("addressbook-organization-update", args=[organization.id])

    with login(client, is_staff=True):
        data = {"name": "new name", "departments": []}
        response = client.post(url, data=data)

    updated_organization = models.Organization.objects.get(id=organization.id)
    assert updated_organization.name == data["name"]

    new_url = reverse("addressbook-organization-list")
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_organization_update_error(client):
    organization = Recipe(models.Organization).make()
    url = reverse("addressbook-organization-update", args=[organization.id])

    data = {}
    with login(client, is_staff=True):
        response = client.post(url, data=data)

    updated_organization = models.Organization.objects.get(id=organization.id)
    assert updated_organization.name == organization.name

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


@pytest.mark.django_db
def test_contact_update_and_redirect(client):
    contact = Recipe(models.Contact).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])

    with login(client, is_staff=True):
        data = {
            "first_name": "first_name",
            "last_name": "last_name",
            "division": "division",
            "phone_no": "phone_no",
            "mobile_no": "mobile_no",
        }
        response = client.post(url, data=data)

    updated_contact = models.Contact.objects.get(id=contact.id)
    assert updated_contact.first_name == data["first_name"]

    new_url = reverse(
        "addressbook-organization-details", args=[contact.organization_id]
    )
    assertRedirects(response, new_url)


# eof
