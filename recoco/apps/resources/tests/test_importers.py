from .. import importers


def test_mediawiki_adater(mocker):
    mwi_class = importers.wiki.MediaWikiRIAdapter

    assert mwi_class.can_handle("my mediawiki generator v3") is True
    assert mwi_class.can_handle("my dokuwiki v7") is False

    mocker.patch("mwclient.Site")
    mocker.patch("mwclient.Site.pages", return_value="Hello", create=True)

    mwi = mwi_class("http://mymediawiki.com")
    assert mwi.load_data() is True

    # Add fake data
    mwi.raw_data = "'''hello'''"
    assert mwi.extract_markdown() == "**hello**\n"
