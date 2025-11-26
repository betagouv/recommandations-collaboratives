from unittest.mock import ANY

import pytest
from django.contrib.sites.models import Site
from django.urls import reverse
from model_bakery import baker

from recoco.utils import login

from ...geomatics.models import Department
from ..models import Contact, Organization


@pytest.mark.django_db
def test_anonymous_can_not_reach_contact_list_endpoint(api_client):
    response = api_client.get(reverse("api-addressbook-contact-list"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_in_user_cannot_list_contacts_or_create(api_client):
    user = baker.make("User")
    api_client.force_authenticate(user)

    url = reverse("api-addressbook-contact-list")

    response = api_client.get(url)
    assert response.status_code == 403

    response = api_client.post(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_in_user_can_read_contact_but_not_update(api_client, current_site):
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
def test_can_not_create_contact_with_wrong_organization(
    api_client, staff_user, current_site
):
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
def test_organization_start_with_filter(
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


@pytest.mark.parametrize(
    "query_params,expected_result",
    [
        ("departments=31", ["vador"]),
        ("departments=31&departments=14", ["vador", "obiwan"]),
        ("departments=33", ["obiwan"]),
        ("departments=69", []),
    ],
)
@pytest.mark.django_db
def test_organization_department(
    api_client, staff_user, current_site, query_params, expected_result
):
    baker.make(Department, code=33, name="Corusant")
    baker.make(Department, code=14, name="Yavin")
    baker.make(Department, code=31, name="Tatoine")

    jedi_organization = baker.make(
        Organization, name="Conseil des Jedi", sites=[current_site]
    )
    jedi_organization.departments.add(33, 14)
    baker.make(
        Contact,
        first_name="obiwan",
        organization=jedi_organization,
        site=current_site,
    )

    sith_organization = baker.make(
        Organization, name="Empire Sith", sites=[current_site]
    )
    sith_organization.departments.add(31)
    baker.make(
        Contact,
        first_name="vador",
        organization=sith_organization,
        site=current_site,
    )

    api_client.force_authenticate(staff_user)
    response = api_client.get(
        f"{reverse('api-addressbook-contact-list')}?{query_params}"
    )
    assert response.status_code == 200
    assert set(contact["first_name"] for contact in response.data["results"]) == set(
        expected_result
    ), f"failure for query: {query_params}"


@pytest.mark.usefixtures("current_site")
class TestInputContactSearch:
    @pytest.fixture(autouse=True)
    def before_after(self, current_site):
        self.current_site = current_site
        yield

    @staticmethod
    def expect_one_not_other(
        api_client, search=None, letter=None, accept=None, refuse=None
    ):
        if refuse is None:
            refuse = []
        if accept is None:
            accept = []
        with login(api_client, groups=["example_com_staff"]):
            url = reverse("api-addressbook-contact-list")
            query = {}
            if letter is not None:
                query["orga-startswith"] = letter
            if search is not None:
                query["search"] = search
            response = api_client.get(url, query)
            ids = [
                search_response["id"] for search_response in response.data["results"]
            ]
            for contact in accept:
                assert contact.id in ids
            for contact in refuse:
                assert contact.id not in ids

    def generate_result(self, first_name, division, org_name=None):
        current_site = self.current_site
        org = (
            baker.make(Organization)
            if org_name is None
            else baker.make(Organization, name=org_name)
        )
        org.sites.add(current_site)
        contact = baker.make(
            Contact,
            first_name=first_name,
            organization=org,
            division=division,
            site=current_site,
        )
        return contact

    @pytest.mark.parametrize(
        "search_terms,expected_result",
        [
            ("skywalker", [999]),
            # ("sky", [999]),  -- specs wants stricter filter, maybe adjust
            ("jedi", [777, 888]),
            ("jed", [777, 888]),
            ("coté obscure", [999]),
            ("obscure", [999]),
            ("Maître", [777, 888]),
            ("maitre", [777, 888]),
        ],
    )
    @pytest.mark.django_db
    def test_contact_search_filter(
        self,
        api_client,
        staff_user,
        current_site,
        search_terms,
        expected_result,
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
            division="Maître Jedi",
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

        response = api_client.get(
            reverse("api-addressbook-contact-list"), {"search": search_terms}
        )

        assert response.status_code == 200
        assert [
            contact["id"] for contact in response.data["results"]
        ] == expected_result, f"failure for search terms: {search_terms}"

    @pytest.mark.django_db
    def test_adac_results(self, api_client, request):
        api_client.login()
        ademe_contact = self.generate_result(
            first_name="Laurent",
            division="Référent Aides travaux et études opérationnelles",
            org_name="ADEME Auvergne-Rhone-Alpes",
        )
        epfl_contact = self.generate_result(
            first_name="Adeline",
            division="Directrice adjointe, responsable pole foncier",
            org_name="EPFL Oise Aisne",
        )
        region_contact = self.generate_result(
            first_name="Valère",
            division="Chargée de mission territoires",
            org_name="Région Grand Est",
        )
        adac_contact = self.generate_result(
            first_name="Éric", division="Président", org_name="ADAC 37"
        )
        self.expect_one_not_other(
            api_client,
            "adac",
            accept=[adac_contact],
            refuse=[ademe_contact, epfl_contact, region_contact],
        )

    @pytest.mark.django_db
    @pytest.mark.skip  # too difficult to differenciate from typo
    def test_adac_22_both_results(self, api_client, request):
        adac_37_contact = self.generate_result(
            first_name="Éric", division="Président", org_name="ADAC 37"
        )
        water_loire_contact = self.generate_result(
            first_name="Délégation Armorique",
            division="(22-29-35-56)",
            org_name="Agence de l'eau Loire-Bretagne",
        )
        self.expect_one_not_other(
            api_client,
            "adac 22",
            accept=[],
            refuse=[adac_37_contact, water_loire_contact],
        )

    @pytest.mark.django_db
    def test_teritoire_not_too_large(self, api_client, request):
        water_loire_contact = self.generate_result(
            first_name="Délégation Armorique",
            division="(22-29-35-56)",
            org_name="Agence de l'eau Loire-Bretagne",
        )
        self.expect_one_not_other(api_client, "teritoire", refuse=[water_loire_contact])

    @pytest.mark.django_db
    def test_jean_compound_names(self, api_client, request):
        # find compound names

        jean_contact = self.generate_result(first_name="Jean", division="")
        jean_fr_contact = self.generate_result(first_name="Jean-François", division="")
        jean_ph_contact = self.generate_result(first_name="Jean-Philippe", division="")
        self.expect_one_not_other(
            api_client, "jean", accept=[jean_contact, jean_ph_contact, jean_fr_contact]
        )

    @pytest.mark.django_db
    @pytest.mark.skip  # too difficult to differenciate from typo
    def test_jean_phi_only_compound(self, api_client, request):
        # prefix

        jean_contact = self.generate_result(first_name="Jean", division="")
        jean_fr_contact = self.generate_result(first_name="Jean-François", division="")
        jean_ph_contact = self.generate_result(first_name="Jean-Philippe", division="")
        self.expect_one_not_other(
            api_client,
            "jean-phi",
            accept=[jean_ph_contact],
            refuse=[jean_contact, jean_fr_contact],
        )

    @pytest.mark.django_db
    def test_sylvain_not_sylvie(self, api_client, request):
        # prefix

        sylvain_contact = self.generate_result(first_name="Sylvain", division="")
        sylvie_contact = self.generate_result(first_name="Sylvie", division="")
        self.expect_one_not_other(
            api_client, "sylvain", accept=[sylvain_contact], refuse=[sylvie_contact]
        )

    @pytest.mark.django_db
    def test_sylva_not_syndicats(self, api_client, request):
        # not too close

        sylvain_contact = self.generate_result(first_name="Sylvain", division="")
        syndicat_contact = self.generate_result(
            first_name="Syndicat d'équipement des communes des Landes",
            division="",
            org_name="SYDEC",
        )
        self.expect_one_not_other(
            api_client, "sylva", accept=[sylvain_contact], refuse=[syndicat_contact]
        )

    @pytest.mark.django_db
    def test_spelling_teritoire(self, api_client, request):
        # typo

        territoire_contact = self.generate_result(
            first_name="Benoît",
            division="Interlocuteur Territoires d'industrie",
            org_name="Banque des Territoires",
        )
        self.expect_one_not_other(api_client, "teritoire", accept=[territoire_contact])

    @pytest.mark.django_db
    def test_ardeche_spelling(self, api_client, request):
        # resilience to typo

        ardeche_contact = self.generate_result(
            first_name="CAUE de l'Ardèche", division="", org_name="CAUE 07"
        )
        self.expect_one_not_other(api_client, "adèche", accept=[ardeche_contact])

    @pytest.mark.django_db
    def test_orga_starts_with(self, api_client, request):
        a_contact = self.generate_result(
            first_name="A", division="", org_name="Agence avec un A"
        )
        b_contact = self.generate_result(
            first_name="B", division="", org_name="Bibliothèque avec un B"
        )
        b_bis_contact = self.generate_result(
            first_name="B",
            division="",
            org_name="Bibliothèque bis avec un B",
        )
        h_contact = self.generate_result(
            first_name="H", division="", org_name="Hôpital avec un H"
        )
        self.expect_one_not_other(
            api_client,
            letter="b",
            accept=[b_contact, b_bis_contact],
            refuse=[h_contact, a_contact],
        )

    @pytest.mark.django_db
    def test_sorting(self, api_client, request):
        a_contact = self.generate_result(
            first_name="Alice", division="", org_name="Assemblée"
        )
        z_contact = self.generate_result(
            first_name="Zoé", division="", org_name="Zassembler"
        )
        search = "zassembler"

        with login(api_client, groups=["example_com_staff"]):
            url = reverse("api-addressbook-contact-list")
            url = f"{url}?search={search}"
            response = api_client.get(url)
            ids = [
                search_response["id"] for search_response in response.data["results"]
            ]
            assert ids[0] == z_contact.id
            assert ids[1] == a_contact.id
