import pytest
from django.contrib.sites.models import Site
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects

from recoco.utils import login

from ..models import Contact, Organization

# Creation


@pytest.mark.django_db
def test_create_organization_not_available_for_non_staff(client):
    Recipe(Organization).make()
    url = reverse("addressbook-organization-create")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_organization_available_for_staff(client):
    Recipe(Organization).make()
    url = reverse("addressbook-organization-create")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_new_organization_and_redirect(request, client, current_site):
    url = reverse("addressbook-organization-create")

    with login(client, groups=["example_com_staff"]):
        data = {"name": "my organization"}
        response = client.post(url, data=data)

    organization = Organization.on_site.first()
    assert organization.name == data["name"]
    assert current_site in list(organization.sites.all())

    new_url = reverse("addressbook-organization-details", args=(organization.pk,))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_organization_list_not_available_for_non_staff(client):
    url = reverse("addressbook-organization-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_existing_organization_and_redirect(current_site, client):
    organization = Recipe(
        Organization, sites=[current_site], name="my organization"
    ).make()
    assert organization.sites.count() == 1

    url = reverse("addressbook-organization-create")

    with login(client, groups=["example_com_staff"]):
        data = {"name": "my organization"}
        response = client.post(url, data=data)

    # no new organization created
    assert Organization.on_site.count() == 1

    updated = Organization.on_site.first()
    assert updated.name == data["name"]
    assert organization.sites.count() == 1
    assert current_site in list(organization.sites.all())

    new_url = reverse("addressbook-organization-details", args=(organization.pk,))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_create_existing_organization_on_other_site_and_redirect(current_site, client):
    other_site = baker.make(Site)

    organization = Recipe(
        Organization, sites=[other_site], name="my organization"
    ).make()
    assert organization.sites.count() == 1

    url = reverse("addressbook-organization-create")

    with login(client, groups=["example_com_staff"]):
        data = {"name": "my organization"}
        response = client.post(url, data=data)

    # no new organization created
    assert Organization.on_site.count() == 1

    updated = Organization.on_site.first()
    assert updated.name == data["name"]
    assert organization.sites.count() == 2
    assert current_site in list(organization.sites.all())

    new_url = reverse("addressbook-organization-details", args=(organization.pk,))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_organization_create_error(client):
    url = reverse("addressbook-organization-create")

    data = {}
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    assert Organization.on_site.count() == 0

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
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_organization_list_only_contains_site_org_w_contacts(
    current_site, client, settings
):
    other = baker.make(Site)

    on_site_no_contacts = Recipe(
        Organization, name="no_contacts", sites=[current_site]
    ).make()
    other_site = Recipe(Organization, name="other_site", sites=[other]).make()
    no_site = Recipe(Organization, name="no_site", sites=[]).make()

    on_site_w_contacts = Recipe(
        Organization, name="on_site_w_contacts", sites=[current_site]
    ).make()
    baker.make(Contact, organization=on_site_w_contacts, site=current_site)

    url = reverse("addressbook-organization-list")

    with settings.SITE_ID.override(current_site.pk):
        with login(client, groups=["example_com_staff"]):
            response = client.get(url)

    assert response.status_code == 200

    assertContains(response, on_site_w_contacts.name)
    assertNotContains(response, on_site_no_contacts.name)
    assertNotContains(response, other_site.name)
    assertNotContains(response, no_site.name)


#
# update


@pytest.mark.django_db
def test_update_organization_not_available_for_non_switchtender_users(client):
    organization = Recipe(Organization).make()
    url = reverse("addressbook-organization-update", args=[organization.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_organization_available_for_switchtender(current_site, client):
    organization = Recipe(Organization, sites=[current_site]).make()
    url = reverse("addressbook-organization-update", args=[organization.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-organization-update"')


@pytest.mark.django_db
def test_organization_update_and_redirect(current_site, client):
    organization = Recipe(Organization, sites=[current_site]).make()
    url = reverse("addressbook-organization-update", args=[organization.id])

    with login(client, groups=["example_com_staff"]):
        data = {"name": "new name", "departments": []}
        response = client.post(url, data=data)

    updated_organization = Organization.on_site.get(id=organization.id)
    assert updated_organization.name == data["name"]

    new_url = reverse("addressbook-organization-list")
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_organization_update_error(current_site, client):
    organization = Recipe(Organization, sites=[current_site]).make()
    url = reverse("addressbook-organization-update", args=[organization.id])

    data = {}
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    updated_organization = Organization.on_site.get(id=organization.id)
    assert updated_organization.name == organization.name

    assert response.status_code == 200
