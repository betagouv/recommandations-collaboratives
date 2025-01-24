from unittest.mock import ANY

import pytest
from django.contrib.sites.models import Site
from django.urls import reverse
from model_bakery import baker
from waffle.testutils import override_switch

from ..models import Contact, Organization


@pytest.mark.django_db
def test_anonymous_can_not_reach_contact_list_endpoint(api_client):
    response = api_client.get(reverse("api-addressbook-contact-list"))
    assert response.status_code == 403


@pytest.mark.django_db
@override_switch("addressbook_contact_use_vector_search", active=True)
def test_non_staff_user_can_list_contacts_but_not_create(api_client):
    user = baker.make("User")
    api_client.force_authenticate(user)

    url = reverse("api-addressbook-contact-list")

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.post(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
@override_switch("addressbook_contact_use_vector_search", active=True)
def test_non_staff_user_can_read_contact_but_not_update(api_client, current_site):
    contact = baker.make(Contact, site=current_site)

    user = baker.make("User")
    api_client.force_authenticate(user)

    url = reverse("api-addressbook-contact-detail", args=[contact.pk])

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.put(url, data={})
    assert response.status_code == 403

    response = api_client.patch(url, data={})
    assert response.status_code == 403

    response = api_client.delete(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
@override_switch("addressbook_contact_use_vector_search", active=True)
def test_staff_user_can_create_contact(api_client, current_site, staff_user):
    organization = baker.make(Organization, sites=[current_site])

    api_client.force_authenticate(staff_user)

    response = api_client.post(
        reverse("api-addressbook-contact-list"),
        data={
            "first_name": "Anakin",
            "last_name": "Skywalker",
            "organization": organization.pk,
        },
    )

    assert response.status_code == 201
    assert response.data == {
        "id": ANY,
        "first_name": "Anakin",
        "last_name": "Skywalker",
        "phone_no": "",
        "mobile_no": "",
        "email": "",
        "division": "",
        "organization": organization.pk,
    }


@pytest.mark.django_db
@override_switch("addressbook_contact_use_vector_search", active=True)
def test_can_not_create_contact_with_wrong_organization(api_client, staff_user):
    other_site = baker.make(Site)
    organization = baker.make(Organization, sites=[other_site])

    api_client.force_authenticate(staff_user)

    response = api_client.post(
        reverse("api-addressbook-contact-list"),
        data={
            "first_name": "Obiwan",
            "last_name": "Kenobi",
            "organization": organization.pk,
        },
    )
    assert response.status_code == 400
    assert (
        str(response.data["organization"])
        == "Organization does not belong to this site"
    )


@pytest.mark.parametrize(
    "search_terms,expected_result",
    [
        ("skywalker", [999]),
        ("jedi", [777, 888]),
        ("maître jedi", [777, 888]),
        ("coté obscure", [999]),
        # On pourrait aller plus loin dans le tests ici,
        # mais à voir avant si on passe par une recherche basée sur watson
    ],
)
@pytest.mark.django_db
@override_switch("addressbook_contact_use_vector_search", active=False)
def test_contact_search_filter(
    api_client, staff_user, current_site, search_terms, expected_result
):

    jedi_organization = baker.make(
        Organization,
        name="Le conseil des Jedi",
        sites=[current_site],
    )
    sith_organization = baker.make(
        Organization,
        name="Le coté obscure de la force",
        sites=[current_site],
    )

    baker.make(
        Contact,
        id=777,
        first_name="Qui-Gon",
        last_name="Jinn",
        organization=jedi_organization,
        division="Maître jedi",
        site=current_site,
    )
    baker.make(
        Contact,
        id=888,
        first_name="Obiwan",
        last_name="Kenobi",
        organization=jedi_organization,
        division="Maître jedi",
        site=current_site,
    )
    baker.make(
        Contact,
        id=999,
        first_name="Anakin",
        last_name="Skywalker",
        organization=sith_organization,
        division="Padawan",
        site=current_site,
    )

    api_client.force_authenticate(staff_user)
    response = api_client.get(
        reverse("api-addressbook-contact-list"), {"search": search_terms}
    )
    assert response.status_code == 200
    assert [
        contact["id"] for contact in response.data["results"]
    ] == expected_result, f"failure for search terms: {search_terms}"
