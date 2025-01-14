import random
import re
import string

import pytest
import requests
import requests_mock
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker
from requests_html import HTMLSession

from .. import importers, models
from ..importers.base import BaseRIAdapter


class LoremIpsumRIAdapter(BaseRIAdapter):
    """A test adapter that creates LoremIpsum resources"""

    URL_PATTERN = "^mock:\\/\\/(www\\.)?lorem-ipsum\\.fr\\/(?P<slug>.*)$"

    @staticmethod
    def can_handle(response: requests.Response):
        return re.match(LoremIpsumRIAdapter.URL_PATTERN, response.url) is not None

    def load_data(self, response: requests.Response):
        return True

    def extract_data(self):
        self.title = "A random generated resource"
        self.content = "".join(
            random.choices(string.ascii_lowercase, k=255)  # noqa: S311
        )


########
# Base Importer
########
@pytest.mark.django_db
def test_already_imported_resource(request):
    current_site = get_current_site(request)

    importer = importers.ResourceImporter()

    uri = "https://somewhere.com"

    resource = baker.make(models.Resource, sites=[current_site], imported_from=uri)

    imported_resource = importer.from_uri(uri)

    assert resource == imported_resource
    assert models.Resource.objects.count() == 1


@pytest.mark.django_db
def test_already_imported_resource_does_not_import_from_other_sites(request):
    current_site = get_current_site(request)

    importer = importers.ResourceImporter()
    importer.ADAPTERS["lorem"] = LoremIpsumRIAdapter

    uri = "mock://lorem-ipsum.fr/test"

    resource = baker.make(models.Resource, imported_from=uri)

    with requests_mock.Mocker() as m:
        m.get(uri, text="lorem ipsum")
        imported_resource = importer.from_uri(uri)

    imported_resource.save()
    imported_resource.sites.add(current_site)

    assert resource != imported_resource
    assert models.Resource.objects.count() == 2


@pytest.mark.django_db
def test_imported_resource_triggers_adapter(request):
    current_site = get_current_site(request)

    importer = importers.ResourceImporter()
    importer.ADAPTERS["lorem"] = LoremIpsumRIAdapter

    uri = "mock://lorem-ipsum.fr/truc"

    with requests_mock.Mocker() as m:
        m.get(uri, text="lorem ipsum")
        resource = importer.from_uri(uri)

    assert resource is not None
    assert resource.title is not None
    assert resource.content is not None

    resource.save()
    resource.sites.add(current_site)

    assert models.Resource.objects.count() == 1


@pytest.mark.django_db
def test_importer_no_uri_matching_adapter(request):
    importer = importers.ResourceImporter()

    uri = "mock://i-dont-know-you.com/"

    with requests_mock.Mocker() as m:
        m.get(uri, text="lorem ipsum")
        resource = importer.from_uri(uri)

    assert resource is None

    assert models.Resource.objects.count() == 0


# -- Mediawiki -- #
def test_mediawiki_adapter(mocker):
    mwi_class = importers.wiki.MediaWikiRIAdapter

    adapter = requests_mock.Adapter()
    session = HTMLSession()
    session.mount("mock", adapter)

    adapter.register_uri(
        "GET", "mock://mymediawiki.com/apage", text=MEDIAWIKI_SAMPLE_PAGE
    )

    response = session.get("mock://mymediawiki.com/apage")

    assert mwi_class.can_handle(response) is True

    # assert mwi_class.can_handle(response) is False

    mwclient_Site = mocker.patch("mwclient.Site")
    mocker.patch("mwclient.Site.pages", return_value="Hello", create=True)

    mwi = mwi_class("mock://mymediawiki.com/apage")
    assert mwi.load_data(response) is True

    mwclient_Site.assert_called_once_with(
        scheme="mock",
        host="mymediawiki.com",
        path="/w/",
        clients_useragent="Recoco MediaWiki Ressource Importer",
    )

    # Add fake data
    mwi.raw_data = "'''hello'''"
    mwi.extract_data()

    assert mwi.content == "**hello**\n"


def test_mediawiki_adapter_with_no_content_header(mocker):
    mwi_class = importers.wiki.MediaWikiRIAdapter

    adapter = requests_mock.Adapter()
    session = HTMLSession()
    session.mount("mock://", adapter)

    adapter.register_uri(
        "GET", "mock://mymediawiki.com/apage", text="<html><head></head></html>"
    )

    response = session.get("mock://mymediawiki.com/apage")

    assert mwi_class.can_handle(response) is False


MEDIAWIKI_SAMPLE_PAGE = """
<!DOCTYPE html>
<html>
<head><meta name='generator' content='mediawiki'>
<link rel="EditURI" type="application/rsd+xml" href="//mymediawiki.com/w/api.php?action=rsd">
</head>
</html>"""


# -- Aides Territoires --
def test_aides_territoires_adapter_handling(mocker, settings):
    mwi_class = importers.api.AidesTerritoiresRIAdapter

    test_uris = [
        (
            "https://aides-territoires.beta.gouv.fr/aides/32cf-sadapter-au-recul-du-trait-de-cote/",
            200,
            SAMPLE_AT_AID,
            True,
        ),
        (
            "https://somewhereelse.com/aides/32cf-sadapter-au-recul-du-trait-de-cote/",
            200,
            "hello",
            False,
        ),
        (
            "https://youcantfind.me/ici",
            404,
            None,
            False,
        ),
    ]

    with requests_mock.Mocker() as m:
        session = HTMLSession()

        for uri, return_code, text, expected in test_uris:
            m.get(uri, status_code=return_code, text=text)
            response = session.get(uri)
            assert mwi_class.can_handle(response) is expected


def test_aides_territoires_adapter_without_key(mocker, settings):
    settings.AIDES_TERRITOIRES_TOKEN = None

    mwi_class = importers.api.AidesTerritoiresRIAdapter

    uri = "https://aides-territoires.beta.gouv.fr/aides/32cf-sadapter-au-recul-du-trait-de-cote/"

    with requests_mock.Mocker() as m:
        session = HTMLSession()

        m.get(uri, text=SAMPLE_AT_AID)

        response = session.get(uri)

        assert mwi_class.can_handle(response) is True

        mwi = mwi_class(uri)
        assert mwi.load_data(response) is False


def test_aides_territoires_adapter(mocker, settings):
    settings.AIDES_TERRITOIRES_TOKEN = "a-fake-token"

    mwi_class = importers.api.AidesTerritoiresRIAdapter

    uri = "https://aides-territoires.beta.gouv.fr/aides/32cf-sadapter-au-recul-du-trait-de-cote/"

    with requests_mock.Mocker() as m:
        m.get(
            uri,
            text="<!DOCTYPE html><html><head></head></html>",
        )

        m.get(
            "https://aides-territoires.beta.gouv.fr/api/aids/32cf-sadapter-au-recul-du-trait-de-cote/",
            status_code=200,
            text=SAMPLE_AT_AID,
        )

        m.post(
            "https://aides-territoires.beta.gouv.fr/api/connexion/",
            json={"token": "my-super-token"},
        )

        session = HTMLSession()
        response = session.get(uri)

        assert mwi_class.can_handle(response) is True

        mwi = mwi_class(uri)
        assert mwi.load_data(response) is True

        mwi.extract_data()

        assert mwi.content is not None


def test_aides_territoires_adapter_with_incomplete_payload(mocker, settings):
    settings.AIDES_TERRITOIRES_TOKEN = "a-fake-token"

    mwi_class = importers.api.AidesTerritoiresRIAdapter

    uri = "https://aides-territoires.beta.gouv.fr/aides/32cf-sadapter-au-recul-du-trait-de-cote/"

    with requests_mock.Mocker() as m:
        m.get(
            uri,
            text="<!DOCTYPE html><html><head></head></html>",
        )

        m.get(
            "https://aides-territoires.beta.gouv.fr/api/aids/32cf-sadapter-au-recul-du-trait-de-cote/",
            status_code=200,
            text=SAMPLE_INCOMPLETE_AT_AID,
        )

        m.post(
            "https://aides-territoires.beta.gouv.fr/api/connexion/",
            json={"token": "my-super-token"},
        )

        session = HTMLSession()
        response = session.get(uri)

        assert mwi_class.can_handle(response) is True

        mwi = mwi_class(uri)
        assert mwi.load_data(response) is True

        mwi.extract_data()

        assert mwi.content is not None


SAMPLE_AT_AID = """{
  "id": "156168",
  "slug": "32cf-sadapter-au-recul-du-trait-de-cote",
  "url": "/aides/32cf-sadapter-au-recul-du-trait-de-cote/",
  "name": "S'adapter au recul du trait de côte",
  "description": "very nice decription",
  "eligibility": "very eligible"
}"""

SAMPLE_INCOMPLETE_AT_AID = """{
  "id": "156168",
  "slug": "32cf-sadapter-au-recul-du-trait-de-cote",
  "url": "/aides/32cf-sadapter-au-recul-du-trait-de-cote/",
  "name": "S'adapter au recul du trait de côte",
  "description": "very nice decription"
}"""
