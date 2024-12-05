from requests_html import HTMLSession

from ..models import Resource
from . import api, wiki


class ResourceImporter:
    """Import external resources as native `Resource` using API or web scraping"""

    ADAPTERS = {
        "mediawiki": wiki.MediaWikiRIAdapter,
        "aides_territoires": api.AidesTerritoiresRIAdapter,
    }

    def from_uri(self, uri):
        session = HTMLSession()

        response = session.get(uri)

        for adapter_class in self.ADAPTERS.values():
            if adapter_class.can_handle(response):
                adapter = adapter_class(uri)
                adapter.load_data(response)
                adapter.extract_data()

                return Resource(
                    status=Resource.TO_REVIEW,
                    title=adapter.title,
                    content=adapter.content,
                    imported_from=uri,
                )

        return None
