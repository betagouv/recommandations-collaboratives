import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertRedirects
from urbanvitaliz.utils import login

from . import models

########################################################################################
# Organization
########################################################################################

# Creation


@pytest.mark.django_db
def test_create_organization_not_available_for_non_switchtender_users(client):
    Recipe(models.Organization).make()
    url = reverse("addressbook-organization-create")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_organization_available_for_switchtender(client):
    Recipe(models.Organization).make()
    url = reverse("addressbook-organization-create")
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


# Listing


@pytest.mark.django_db
def test_organization_list_not_available_for_non_switchtender(client):
    url = reverse("addressbook-organization-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_organization_list_available_for_switchtender(client):
    url = reverse("addressbook-organization-list")
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_organization_create_and_redirect(client):
    url = reverse("addressbook-organization-create")

    with login(client, groups=["switchtender"]):
        data = {"name": "my organization"}
        response = client.post(url, data=data)

    organization = models.Organization.objects.all()[0]
    assert organization.name == data["name"]

    new_url = reverse("addressbook-organization-list")
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_organization_create_error(client):
    url = reverse("addressbook-organization-create")

    data = {}
    with login(client, groups=["switchtender"]):
        response = client.post(url, data=data)

    assert models.Organization.objects.count() == 0

    assert response.status_code == 200


#
# update


@pytest.mark.django_db
def test_update_organization_not_available_for_non_switchtender_users(client):
    organization = Recipe(models.Organization).make()
    url = reverse("addressbook-organization-update", args=[organization.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_organization_available_for_switchtender(client):
    organization = Recipe(models.Organization).make()
    url = reverse("addressbook-organization-update", args=[organization.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-organization-update"')


@pytest.mark.django_db
def test_organization_update_and_redirect(client):
    organization = Recipe(models.Organization).make()
    url = reverse("addressbook-organization-update", args=[organization.id])

    with login(client, groups=["switchtender"]):
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
    with login(client, groups=["switchtender"]):
        response = client.post(url, data=data)

    updated_organization = models.Organization.objects.get(id=organization.id)
    assert updated_organization.name == organization.name

    assert response.status_code == 200


########################################################################################
# Contact
########################################################################################

# Creation


@pytest.mark.django_db
def test_create_contact_not_available_for_non_switchtender(client):
    organization = Recipe(models.Organization).make()
    url = reverse(
        "addressbook-organization-contact-create",
        args=[organization.id],
    )
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_contact_available_for_switchtender(client):
    organization = Recipe(models.Organization).make()
    url = reverse(
        "addressbook-organization-contact-create",
        args=[organization.id],
    )
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-contact-create"')


@pytest.mark.django_db
def test_contact_create_and_redirect(client):
    organization = Recipe(models.Organization).make()
    url = reverse("addressbook-organization-contact-create", args=[organization.id])

    with login(client, groups=["switchtender"]):
        data = {"first_name": "my contact"}
        response = client.post(url, data=data)

    contact = models.Contact.on_site.all()[0]
    assert contact.first_name == data["first_name"]

    new_url = reverse("addressbook-organization-details", args=[organization.id])
    assertRedirects(response, new_url)


#
# update


@pytest.mark.django_db
def test_update_contact_not_available_for_non_switchtender(client):
    contact = Recipe(models.Contact).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_contact_available_for_switchtender(request, client):
    contact = Recipe(models.Contact, site=get_current_site(request)).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-contact-update"')


@pytest.mark.django_db
def test_contact_update_and_redirect(request, client):
    contact = Recipe(models.Contact, site=get_current_site(request)).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])

    with login(client, groups=["switchtender"]):
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
