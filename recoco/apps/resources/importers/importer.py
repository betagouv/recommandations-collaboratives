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
        """
        Given a uri, try to import the related content if we have a registered
        importer able to do it.
        """

        # If we already have this resource, don't fetch it
        try:
            return Resource.on_site.get(imported_from=uri)
        except Resource.DoesNotExist:
            pass

        session = HTMLSession()

        response = session.get(uri)

        for adapter_class in self.ADAPTERS.values():
            if adapter_class.can_handle(response):
                adapter = adapter_class(uri)
                if not adapter.load_data(response):
                    continue

                adapter.extract_data()

                return Resource(
                    status=Resource.TO_REVIEW,
                    title=adapter.title,
                    content=adapter.content,
                    imported_from=uri,
                )

        return None
