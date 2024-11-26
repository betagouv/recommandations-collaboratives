import logging
import re

import requests
import requests_jwt
from django.conf import settings

from .base import BaseRIAdapter

LOGGER = logging.getLogger("recoco.apps.resources")


class AidesTerritoiresRIAdapter(BaseRIAdapter):
    """Adapter for website Aides Territoires"""

    @staticmethod
    def can_handle(response: requests.Response):
        # example : https://aides-territoires.beta.gouv.fr/aides/32cf-sadapter-au-recul-du-trait-de-cote/
        url_pattern = "^https?:\\/\\/(www\\.)?aides-territoires\\.beta\\.gouv\\.fr\\/aides\\/(.*)$"

        return re.match(url_pattern, response.url) is not None

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

        token = cnx_response.json()["token"]
        auth = requests_jwt.JWTAuth(token)
        response = requests.get(
            "https://aides-territoires.beta.gouv.fr/api/aids/", auth=auth, timeout=5
        )

        self.raw_data = response.json

        return True

    def extract_data(self):
        pass
