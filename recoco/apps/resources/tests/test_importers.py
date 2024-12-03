import requests_mock
from requests_html import HTMLSession

from .. import importers


def test_mediawiki_adapter(mocker):
    mwi_class = importers.wiki.MediaWikiRIAdapter

    adapter = requests_mock.Adapter()
    session = HTMLSession()
    session.mount("mock://", adapter)

    adapter.register_uri(
        "GET",
        "mock://mymediawiki.com/apage",
        text="<!DOCTYPE html><html><head><meta name='generator' content='mediawiki'></head></html>",
    )

    response = session.get("mock://mymediawiki.com/apage")

    assert mwi_class.can_handle(response) is True

    # assert mwi_class.can_handle(response) is False

    mocker.patch("mwclient.Site")
    mocker.patch("mwclient.Site.pages", return_value="Hello", create=True)

    mwi = mwi_class("mock://mymediawiki.com/apage")
    assert mwi.load_data() is True

    # Add fake data
    mwi.raw_data = "'''hello'''"
    mwi.extract_data()

    assert mwi.content == "**hello**\n"


def test_aides_territoires_adapter(mocker):
    mwi_class = importers.api.AidesTerritoiresRIAdapter

    uri = "https://aides-territoires.beta.gouv.fr/aides/aide-imaginaire/"
    api_uri = "https://aides-territoires.beta.gouv.fr/api/aids/aide-imaginaire/"

    adapter = requests_mock.Adapter()
    session = HTMLSession()
    session.mount("https://", adapter)

    adapter.register_uri(
        "GET",
        uri,
        text="<!DOCTYPE html><html><head></head></html>",
    )

    adapter.register_uri(
        "GET",
        api_uri,
        text=SAMPLE_AT_AID,
    )

    response = session.get(uri)

    assert mwi_class.can_handle(response) is True

    mwi = mwi_class(uri)
    assert mwi.load_data() is True

    mwi.extract_data()

    assert mwi.content is not None


SAMPLE_AT_AID = """{
    "@context": "string",
    "@id": "string",
    "@type": "string",
    "name": "string",
    "description": "string",
    "status": "string",
    "origin_url": "https://appelsaprojets.ademe.fr/aap/AURASTC2019-54",
    "aid_audiences": "commune",
    "aid_types": "grant",
    "aid_destinations": "supply",
    "date_start": "2024-12-02T13:30:57.225Z",
    "date_predeposit": "2024-12-02T13:30:57.225Z",
    "date_submission_deadline": "2023-05-30",
    "time_create": "2024-12-02T13:30:57.225Z"
}"""
