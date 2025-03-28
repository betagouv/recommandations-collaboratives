import logging
import re

import pandoc
import requests
from django.conf import settings

from .base import BaseRIAdapter

LOGGER = logging.getLogger("recoco.apps.resources")


class AidesTerritoiresRIAdapter(BaseRIAdapter):
    """Adapter for website Aides Territoires"""

    URL_PATTERN = (
        # example : https://aides-territoires.beta.gouv.fr/aides/32cf-sadapter-au-recul-du-trait-de-cote/
        "^https?:\\/\\/(www\\.)?aides-territoires\\.beta\\.gouv\\.fr\\/aides\\/(?P<slug>.*)$"
    )

    @staticmethod
    def can_handle(response: requests.Response):
        return re.match(AidesTerritoiresRIAdapter.URL_PATTERN, response.url) is not None

    def _extract_pageslug_from_url(self, url):
        groups = re.match(self.URL_PATTERN, url)

        return groups["slug"]

    def load_data(self, response: requests.Response):
        at_token = getattr(settings, "AIDES_TERRITOIRES_TOKEN", None)
        if not at_token:
            LOGGER.error("No AIDES_TERRITOIRES_TOKEN defined, no request will succeed!")
            return False

        cnx_response = requests.post(
            "https://aides-territoires.beta.gouv.fr/api/connexion/",
            headers={"X-Auth-Token": at_token},
            timeout=5,
        )

        if not cnx_response.ok:
            return False

        token = cnx_response.json()["token"]

        pageslug = self._extract_pageslug_from_url(self.uri)
        uri = f"https://aides-territoires.beta.gouv.fr/api/aids/{pageslug}"

        response = requests.get(
            uri,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=5,
        )

        if not response.ok:
            return False

        self.raw_data = response.json()

        return True

    def _clean_at_section(self, html: str):
        """Remove styles, ids, and external item from html tags"""
        if not html:
            return None

        doc = pandoc.read(html, format="html")

        return pandoc.write(doc, format="markdown_strict")

    def extract_data(self):
        self.title = self.raw_data.get("name", "Sans Nom")

        sections = (
            ("description", "Description"),
            ("eligibility", "Critères d'éligibilité"),
        )

        self.content = ""
        for section_key, section_title in sections:
            section_content = self._clean_at_section(
                self.raw_data.get(section_key, None)
            )
            if section_content:
                self.content += f"""## {section_title}\n\n{section_content}\n\n"""
