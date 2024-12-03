import logging
import re

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

    def load_data(self):
        at_token = getattr(settings, "AIDES_TERRITOIRES_TOKEN", None)
        if not at_token:
            LOGGER.warning(
                "No AIDES_TERRITOIRES_TOKEN defined, no request will succeed!"
            )

        cnx_response = requests.post(
            "https://aides-territoires.beta.gouv.fr/api/connexion/",
            headers={"X-Auth-Token": at_token},
            timeout=5,
        )  # FIXME

        if not cnx_response.ok:
            return False

        pageslug = self._extract_pageslug_from_url(self.uri)

        token = cnx_response.json()["token"]
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

    def extract_data(self):
        data = self.raw_data

        self.title = data["name"]
        self.content = data["description"]
