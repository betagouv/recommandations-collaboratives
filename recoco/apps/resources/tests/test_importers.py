import requests_mock
from requests_html import HTMLSession

from .. import importers


def test_mediawiki_adapter(mocker):
    mwi_class = importers.wiki.MediaWikiRIAdapter

    adapter = requests_mock.Adapter()
    session = HTMLSession()
    session.mount("mock://", adapter)

    adapter.register_uri(
        "GET", "mock://mymediawiki.com/apage", text=MEDIAWIKI_SAMPLE_PAGE
    )

    response = session.get("mock://mymediawiki.com/apage")

    assert mwi_class.can_handle(response) is True

    # assert mwi_class.can_handle(response) is False

    mocker.patch("mwclient.Site")
    mocker.patch("mwclient.Site.pages", return_value="Hello", create=True)

    mwi = mwi_class("mock://mymediawiki.com/apage")
    assert mwi.load_data(response) is True

    # Add fake data
    mwi.raw_data = "'''hello'''"
    mwi.extract_data()

    assert mwi.content == "**hello**\n"


MEDIAWIKI_SAMPLE_PAGE = """
<!DOCTYPE html>
<html>
<head><meta name='generator' content='mediawiki'>
<link rel="EditURI" type="application/rsd+xml" href="//mymediawiki.com/w/api.php?action=rsd">
</head>
</html>"""


def test_aides_territoires_adapter(mocker):
    mwi_class = importers.api.AidesTerritoiresRIAdapter

    uri = "https://aides-territoires.beta.gouv.fr/aides/32cf-sadapter-au-recul-du-trait-de-cote/"
    api_uri = "https://aides-territoires.beta.gouv.fr/api/aids/32cf-sadapter-au-recul-du-trait-de-cote/"

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
    assert mwi.load_data(response) is True

    mwi.extract_data()

    assert mwi.content is not None


SAMPLE_AT_AID = """{
{
  "id": 156168,
  "slug": "32cf-sadapter-au-recul-du-trait-de-cote",
  "url": "/aides/32cf-sadapter-au-recul-du-trait-de-cote/",
  "name": "S'adapter au recul du trait de c\u00f4te",
  "name_initial": "Accompagnement pour l\u2019adaptation des territoires littoraux au recul du trait de c\u00f4te - AXE 2",
  "short_title": null,
  "financers": ["Minist\u00e8re de la Transition \u00e9cologique et de la Coh\u00e9sion des territoires"],
  "financers_full": [{ "id": 26, "name": "Minist\u00e8re de la Transition \u00e9cologique et de la Coh\u00e9sion des territoires", "logo": "https://aides-territoires-prod.s3.fr-par.scw.cloud/aides-territoires-prod/backers/ministere-de-la-transition-ecologique-et-solidaire_logo.png" }],
  "instructors": ["Pr\u00e9fectures de d\u00e9partement"],
  "instructors_full": [{ "id": 429, "name": "Pr\u00e9fectures de d\u00e9partement", "logo": null }],
  "programs": ["Fonds vert - \u00c9dition 2024"],
  "description": "<p>\r\n <strong>\r\n  Ambition \u00e9cologique du projet financ\u00e9\r\n </strong>\r\n</p>\r\n<p><span style=\"text-align: justify;\">Dans un objectif d\u2019adaptation au changement climatique, les projets financ\u00e9s par le fonds vert doivent permettre de soutenir les collectivit\u00e9s dans la mise en \u0153uvre d\u2019op\u00e9rations d\u2019anticipation et d\u2019adaptation aux effets du changement climatique et au recul du trait de c\u00f4te.</span></p><p><strong style=\"background-color: var(--body-bg); color: var(--text-color); font-family: var(--font-family-base); font-size: var(--font-size-base); text-align: var(--bs-body-text-align);\">\u2192\r\n  <em>\r\n   Cette mesure peut s'articuler avec d'autres dispositifs : voir le d\u00e9tail dans le cahier d'accompagnement.</em></strong><br></p>",
  "perimeter": "Communes littorales",
  "perimeter_scale": "Ad-hoc"
}"""
