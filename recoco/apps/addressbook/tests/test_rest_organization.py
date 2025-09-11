import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker

from recoco.utils import login

from ..models import Contact, Organization, OrganizationGroup


@pytest.fixture
def acme_organization(current_site):
    organization = baker.make(
        Organization, name="acme corporation", sites=[current_site]
    )
    baker.make(Contact, organization=organization)
    return organization


@pytest.mark.django_db
def test_anonymous_can_list_organizations_but_not_create(api_client):
    url = reverse("api-addressbook-organization-list")

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.post(url, data={})
    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_can_search_organizations(api_client, acme_organization):
    url = reverse("api-addressbook-organization-list")
    response = api_client.get(url, {"search": "acme"})

    assert response.status_code == 200
    assert len(response.data) > 0


@pytest.mark.django_db
def test_anonymous_can_read_organization_but_not_update(api_client, acme_organization):
    url = reverse("api-addressbook-organization-detail", args=[acme_organization.pk])

    response = api_client.get(url)
    assert response.status_code == 200

    response = api_client.put(url, data={})
    assert response.status_code == 403

    response = api_client.patch(url, data={})
    assert response.status_code == 403

    response = api_client.delete(url, data={})
    assert response.status_code == 403


class TestOrganizationSearch:
    @staticmethod
    def expect_one_not_other(
        api_client, search=None, letter=None, accept=None, refuse=None
    ):
        if refuse is None:
            refuse = []
        if accept is None:
            accept = []
        with login(api_client):
            url = reverse("api-addressbook-contact-list") + "?"
            if letter is not None:
                url += f"orga-startswith={letter}&"
            if search is not None:
                url += f"search={search}"
            response = api_client.get(f"{url}?search={search}")
            ids = [
                search_response["id"] for search_response in response.data["results"]
            ]
            for contact in accept:
                assert contact.id in ids
            for contact in refuse:
                assert contact.id not in ids

    @staticmethod
    def generate_result(site, first_name, division, org_name=None):
        org = (
            baker.make(Organization, sites=[site])
            if org_name is None
            else baker.make(Organization, name=org_name, sites=[site])
        )
        contact = baker.make(
            Contact,
            first_name=first_name,
            organization=org,
            division=division,
            site=site,
        )
        return contact

    @pytest.mark.django_db
    def test_have_results(self, api_client, request):
        site = get_current_site(request)
        self.generate_result(
            site=site,
            first_name="Laurent",
            division="Référent Aides travaux et études opérationnelles",
            org_name="ADEME Auvergne-Rhone-Alpes",
        )
        self.generate_result(
            site=site,
            first_name="Adeline",
            division="Directrice adjointe, responsable pole foncier",
            org_name="EPFL Oise Aisne",
        )
        self.generate_result(
            site=site,
            first_name="Valère",
            division="Chargée de mission territoires",
            org_name="Région Grand Est",
        )
        self.generate_result(
            site=site, first_name="Éric", division="Président", org_name="ADAC 37"
        )
        contacts_nb = Contact.objects.count()
        assert contacts_nb == 4

    @pytest.mark.django_db
    def test_adac_results(self, api_client, request):
        site = get_current_site(request)
        ademe_contact = self.generate_result(
            site=site,
            first_name="Laurent",
            division="Référent Aides travaux et études opérationnelles",
            org_name="ADEME Auvergne-Rhone-Alpes",
        )
        epfl_contact = self.generate_result(
            site=site,
            first_name="Adeline",
            division="Directrice adjointe, responsable pole foncier",
            org_name="EPFL Oise Aisne",
        )
        region_contact = self.generate_result(
            site=site,
            first_name="Valère",
            division="Chargée de mission territoires",
            org_name="Région Grand Est",
        )
        adac_contact = self.generate_result(
            site=site, first_name="Éric", division="Président", org_name="ADAC 37"
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
        site = get_current_site(request)
        adac_37_contact = self.generate_result(
            site=site, first_name="Éric", division="Président", org_name="ADAC 37"
        )
        water_loire_contact = self.generate_result(
            site=site,
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
        site = get_current_site(request)
        water_loire_contact = self.generate_result(
            site=site,
            first_name="Délégation Armorique",
            division="(22-29-35-56)",
            org_name="Agence de l'eau Loire-Bretagne",
        )
        self.expect_one_not_other(api_client, "teritoire", refuse=[water_loire_contact])

    @pytest.mark.django_db
    def test_jean_compound_names(self, api_client, request):
        # find compound names
        site = get_current_site(request)
        jean_contact = self.generate_result(site=site, first_name="Jean", division="")
        jean_fr_contact = self.generate_result(
            site=site, first_name="Jean-François", division=""
        )
        jean_ph_contact = self.generate_result(
            site=site, first_name="Jean-Philippe", division=""
        )
        self.expect_one_not_other(
            api_client, "jean", accept=[jean_contact, jean_ph_contact, jean_fr_contact]
        )

    @pytest.mark.django_db
    @pytest.mark.skip  # too difficult to differenciate from typo
    def test_jean_phi_only_compound(self, api_client, request):
        # prefix
        site = get_current_site(request)
        jean_contact = self.generate_result(site=site, first_name="Jean", division="")
        jean_fr_contact = self.generate_result(
            site=site, first_name="Jean-François", division=""
        )
        jean_ph_contact = self.generate_result(
            site=site, first_name="Jean-Philippe", division=""
        )
        self.expect_one_not_other(
            api_client,
            "jean-phi",
            accept=[jean_ph_contact],
            refuse=[jean_contact, jean_fr_contact],
        )

    @pytest.mark.django_db
    def test_sylvain_not_sylvie(self, api_client, request):
        # prefix
        site = get_current_site(request)
        sylvain_contact = self.generate_result(
            site=site, first_name="Sylvain", division=""
        )
        sylvie_contact = self.generate_result(
            site=site, first_name="Sylvie", division=""
        )
        self.expect_one_not_other(
            api_client, "sylvain", accept=[sylvain_contact], refuse=[sylvie_contact]
        )

    @pytest.mark.django_db
    def test_sylva_not_syndicats(self, api_client, request):
        # not too close
        site = get_current_site(request)
        sylvain_contact = self.generate_result(
            site=site, first_name="Sylvain", division=""
        )
        syndicat_contact = self.generate_result(
            site=site,
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
        site = get_current_site(request)
        territoire_contact = self.generate_result(
            site=site,
            first_name="Benoît",
            division="Interlocuteur Territoires d'industrie",
            org_name="Banque des Territoires",
        )
        self.expect_one_not_other(api_client, "teritoire", accept=[territoire_contact])

    @pytest.mark.django_db
    def test_ardeche_spelling(self, api_client, request):
        # resilience to typo
        site = get_current_site(request)
        ardeche_contact = self.generate_result(
            site=site, first_name="CAUE de l'Ardèche", division="", org_name="CAUE 07"
        )
        self.expect_one_not_other(api_client, "adèche", accept=[ardeche_contact])

    @pytest.mark.django_db
    def test_orga_starts_with(self, api_client, request):
        site = get_current_site(request)
        a_contact = self.generate_result(
            site=site, first_name="", division="", org_name="Agence avec un A"
        )
        b_contact = self.generate_result(
            site=site, first_name="", division="", org_name="Bibliothèque avec un B"
        )
        b_bis_contact = self.generate_result(
            site=site, first_name="", division="", org_name="Bibliothèque bis avec un B"
        )
        h_contact = self.generate_result(
            site=site, first_name="", division="", org_name="Hôpital avec un H"
        )
        self.expect_one_not_other(
            api_client,
            letter="b",
            accept=[b_contact, b_bis_contact],
            refuse=[h_contact, a_contact],
        )

    @pytest.mark.django_db
    def test_sorting(self, api_client, request):
        site = get_current_site(request)
        a_contact = self.generate_result(
            site=site, first_name="Alice", division="", org_name="Assemblée"
        )
        z_contact = self.generate_result(
            site=site, first_name="Zoé", division="", org_name="Zassembler"
        )
        search = "zassembler"

        with login(api_client):
            url = reverse("api-addressbook-contact-list")
            url = f"{url}?search={search}"
            response = api_client.get(url)
            ids = [
                search_response["id"] for search_response in response.data["results"]
            ]
            assert ids[0] == z_contact.id
            assert ids[1] == a_contact.id

    @pytest.mark.django_db
    def test_orga_search(self, api_client, request):
        site = get_current_site(request)
        baker.make(Organization, sites=[site], name="ademe")
        z_org = baker.make(Organization, sites=[site], name="zoologie")
        search = "zoo"

        with login(api_client):
            url = reverse("api-addressbook-organization-list")
            url = f"{url}?search={search}"
            response = api_client.get(url)
            ids = [
                search_response["id"] for search_response in response.data["results"]
            ]
            assert ids == [z_org.id]

    @pytest.mark.django_db
    def test_orga_group_search(self, api_client, request):
        baker.make(OrganizationGroup, name="ademe")
        z_org = baker.make(OrganizationGroup, name="zoologie")
        search = "zoo"

        with login(api_client):
            url = reverse("api-addressbook-organization-group-list")
            url = f"{url}?search={search}"
            response = api_client.get(url)
            ids = [
                search_response["id"] for search_response in response.data["results"]
            ]
            assert ids == [z_org.id]
