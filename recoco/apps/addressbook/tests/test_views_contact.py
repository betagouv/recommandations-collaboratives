import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertRedirects

from recoco.utils import login

from ..models import Contact, Organization


# Contact list
@pytest.mark.django_db
def test_contact_list_not_available_for_non_staff(client):
    url = reverse("addressbook-contact-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_contact_list_available(client, current_site):
    url = reverse("addressbook-contact-list")
    with login(client) as user:
        assign_perm("sites.change_addressbook", user, current_site)
        response = client.get(url)

    assert response.status_code == 200


# Creation


@pytest.mark.django_db
def test_create_contact_not_available_for_non_switchtender(client):
    organization = Recipe(Organization).make()
    url = reverse(
        "addressbook-organization-contact-create",
        args=[organization.id],
    )
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_contact_available_for_switchtender(client):
    organization = Recipe(Organization).make()
    url = reverse(
        "addressbook-organization-contact-create",
        args=[organization.id],
    )
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-contact-create"')


@pytest.mark.django_db
def test_contact_create_and_redirect(request, client):
    current_site = get_current_site(request)

    organization = Recipe(Organization, sites=[current_site]).make()
    url = reverse("addressbook-organization-contact-create", args=[organization.id])

    with login(client, groups=["example_com_staff"]):
        data = {"first_name": "my contact"}
        response = client.post(url, data=data)

    contact = Contact.on_site.all()[0]
    assert contact.first_name == data["first_name"]

    new_url = reverse("addressbook-organization-details", args=[organization.id])
    assertRedirects(response, new_url)


# update


@pytest.mark.django_db
def test_update_contact_not_available_for_non_switchtender(client):
    contact = Recipe(Contact).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_contact_available_for_switchtender(request, client):
    contact = Recipe(Contact, site=get_current_site(request)).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-contact-update"')


@pytest.mark.django_db
def test_contact_update_and_redirect(request, client):
    current_site = get_current_site(request)

    contact = Recipe(
        Contact, organization__sites=[current_site], site=current_site
    ).make()
    url = reverse("addressbook-organization-contact-update", args=[contact.id])

    with login(client, groups=["example_com_staff"]):
        data = {
            "first_name": "first_name",
            "last_name": "last_name",
            "division": "division",
            "phone_no": "phone_no",
            "mobile_no": "mobile_no",
        }
        response = client.post(url, data=data)

    updated_contact = Contact.on_site.get(id=contact.id)
    assert updated_contact.first_name == data["first_name"]

    new_url = reverse(
        "addressbook-organization-details", args=[contact.organization_id]
    )
    assertRedirects(response, new_url)
