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

    uri = "https://aides-territoires.beta.gouv.fr/aides/passeurs-dimages-en-bourgogne-franche-comte/"

    adapter = requests_mock.Adapter()
    session = HTMLSession()
    session.mount("https://", adapter)

    adapter.register_uri(
        "GET",
        uri,
        text="<!DOCTYPE html><html><head></head></html>",
    )

    response = session.get(uri)

    assert mwi_class.can_handle(response) is True
    # assert mwi_class.can_handle("my dokuwiki v7") is False

    mocker.patch("mwclient.Site")
    mocker.patch("mwclient.Site.pages", return_value="Hello", create=True)

    mwi = mwi_class(uri)
    assert mwi.load_data() is True
    assert mwi.extract_data()

    # Add fake data
    mwi.raw_data = "'''hello'''"
