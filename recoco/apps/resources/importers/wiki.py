from urllib.parse import unquote, urlparse

import mwclient
import pandoc
import requests
from bs4 import BeautifulSoup

from .base import BaseRIAdapter


class MediaWikiRIAdapter(BaseRIAdapter):
    @staticmethod
    def can_handle(response: requests.Response) -> bool:
        generator = response.html.find("head > meta[name='generator']", first=True)
        if not generator:
            return False

        generator = generator.attrs["content"].lower()

        return "mediawiki" in generator

    def load_data(self, response) -> bool:
        edit_uri = response.html.find('head > link[rel="EditURI"]', first=True).attrs[
            "href"
        ]
        parsed_edit_uri = urlparse(edit_uri)
        parsed_edit_uri = parsed_edit_uri._replace(
            scheme=self.parsed_uri.scheme, query=""
        )

        api_url = parsed_edit_uri

        site = mwclient.Site(
            scheme=api_url.scheme,
            host=api_url.netloc,
            path=api_url.path.removesuffix("api.php"),
            clients_useragent="Recoco MediaWiki Ressource Importer",
        )
        self.page_name = unquote(self.parsed_uri.path.rsplit("/", 1)[-1])

        page = site.pages[self.page_name]
        if page.exists:
            self.raw_data = page.text(expandtemplates=True)

        return True

    def extract_data(self) -> None:
        doc = pandoc.read(self.raw_data, format="mediawiki")

        self.title = self.page_name.replace("_", " ").capitalize()
        content = pandoc.write(doc, format="markdown_strict")

        # clean up useless tags (div, span, img)
        self.content = BeautifulSoup(content).get_text()
