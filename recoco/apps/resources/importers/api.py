import re

import requests

from .base import BaseRIAdapter


class AidesTerritoiresRIAdapter(BaseRIAdapter):
    """Adapter for website Aides Territoires"""

    @staticmethod
    def can_handle(response: requests.Response):
        # example : https://aides-territoires.beta.gouv.fr/aides/32cf-sadapter-au-recul-du-trait-de-cote/
        url_pattern = "^https?:\\/\\/(?:www\\.)aides-territoires\\.fr\\/aides\\/*)$"

        m = re.match(url_pattern, response.url)
        if m:
            return True

        return False

    def load_data(self):
        pass

    def extract_markdown(self):
        pass
