from urllib.parse import unquote

import mwclient
import pandoc
import requests

from .base import BaseRIAdapter


class MediaWikiRIAdapter(BaseRIAdapter):
    @staticmethod
    def can_handle(response: requests.Response):
        generator = response.html.find("head > meta[name='generator']", first=True)
        generator = generator.attrs["content"].lower()

        return "mediawiki" in generator

    def load_data(self):
        site = mwclient.Site(
            f"{self.parsed_uri.netloc}",
            path="/",
            clients_useragent="Recoco MediaWiki Ressource Importer",
        )
        self.page_name = unquote(self.parsed_uri.path.rsplit("/", 1)[-1])

        page = site.pages[self.page_name]
        if page.exists:
            self.raw_data = page.text(expandtemplates=True)

        return True

    def extract_data(self):
        doc = pandoc.read(self.raw_data, format="mediawiki")

        self.title = unquote(self.parsed_uri.path.rsplit("/", 1)[-1])
        self.content = pandoc.write(doc, format="markdown_strict")
