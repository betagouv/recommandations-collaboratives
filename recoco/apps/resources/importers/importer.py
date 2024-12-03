from requests_html import HTMLSession

from ..models import Resource
from . import wiki


class ResourceImporter:
    """Import external resources as native `Resource` using API or web scraping"""

    ADAPTERS = {"mediawiki": wiki.MediaWikiRIAdapter}

    def from_uri(self, uri):
        session = HTMLSession()

        response = session.get(uri)

        for adapter_class in self.ADAPTERS.values():
            if adapter_class.can_handle(response):
                adapter = adapter_class(uri)
                adapter.load_data()
                adapter.extract_data()

                return Resource(
                    title=adapter.title, content=adapter.content, imported_from=uri
                )

        return None
