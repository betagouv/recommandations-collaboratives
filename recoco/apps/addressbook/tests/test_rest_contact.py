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
def test_non_staff_user_can_list_contacts_but_not_create(api_client):
    user = baker.make("User")
    api_client.force_authenticate(user)

    url = reverse("api-addressbook-contact-list")

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.post(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
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
        "created": ANY,
        "modified": ANY,
    }


@pytest.mark.django_db
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
    "search_terms,expected_result,use_watson",
    [
        # vector search
        ("skywalker", [999], False),
        ("jedi", [777, 888], False),
        ("coté obscure", [999], False),
        ("cote", [999], False),
        ("Maître", [777, 888], False),
        ("maitre", [777, 888], False),
        # watson search
        ("skywalker", [999], True),
        ("jedi", [777, 888], True),
        ("coté obscure", [999], True),
        ("cote", [999], True),
        ("Maître", [777, 888], True),
        ("maitre", [777, 888], True),
    ],
)
@pytest.mark.django_db
def test_contact_search_filter(
    api_client,
    staff_user,
    current_site,
    search_terms,
    expected_result,
    use_watson,
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
        email="quiqui@coruscant.com",
        organization=jedi_organization,
        division="Maître jedi",
        site=current_site,
    )
    baker.make(
        Contact,
        id=888,
        first_name="Obiwan",
        last_name="Kenobi",
        email="obi@tatooine.com",
        organization=jedi_organization,
        division="Maître",
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

    with override_switch("addressbook_contact_use_watson_search", active=use_watson):
        response = api_client.get(
            reverse("api-addressbook-contact-list"), {"search": search_terms}
        )

    assert response.status_code == 200
    assert [
        contact["id"] for contact in response.data["results"]
    ] == expected_result, f"failure for search terms: {search_terms}"


@pytest.mark.parametrize(
    "filter_value,expected_result",
    [
        ("E", ["vador"]),
        ("e", ["vador"]),
        ("C", ["obiwan"]),
        ("conseil", ["obiwan"]),
        ("Z", []),
    ],
)
@pytest.mark.django_db
def test_organization_group_filter(
    api_client, staff_user, current_site, filter_value, expected_result
):
    jedi_organization = baker.make(
        Organization, name="Conseil des Jedi", sites=[current_site]
    )
    baker.make(
        Contact,
        first_name="obiwan",
        organization=jedi_organization,
        site=current_site,
    )

    sith_organization = baker.make(
        Organization, name="Empire Sith", sites=[current_site]
    )
    baker.make(
        Contact,
        first_name="vador",
        organization=sith_organization,
        site=current_site,
    )

    api_client.force_authenticate(staff_user)
    response = api_client.get(
        f"{reverse('api-addressbook-contact-list')}?orga-startswith={filter_value}"
    )
    assert response.status_code == 200
    assert [
        contact["first_name"] for contact in response.data["results"]
    ] == expected_result, f"failure for filter value: {filter_value}"
