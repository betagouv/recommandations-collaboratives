from requests_html import HTMLSession

from ..models import Resource
from . import wiki


class ResourceImporter:
    """Import external resources as native `Resource` using API or web scraping"""

    ADAPTERS = {"mediawiki": wiki.MediaWikiRIAdapter}

    def from_uri(self, uri):
        session = HTMLSession()

        response = session.get(uri)

        generator = response.html.find("head > meta[name='generator']", first=True)
        generator = generator.attrs["content"].lower()

        for adapter_class in self.ADAPTERS:
            if adapter_class.can_handle(generator):
                adapter = adapter_class(uri)
                adapter.load_data()
                markdown = adapter.extract_markdown()

                return Resource(content=markdown)

        return None
