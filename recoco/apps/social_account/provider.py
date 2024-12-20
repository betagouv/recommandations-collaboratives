from allauth.socialaccount.providers.openid_connect.provider import (
    OpenIDConnectProvider,
)
from django.utils.crypto import get_random_string


class ProConnectProvider(OpenIDConnectProvider):
    id = "proconnect"
    name = "ProConnect"

    def get_auth_params(self):
        return super().get_auth_params() | {
            "nonce": get_random_string(32),
            "acr_values": "eidas1",
        }

    def extract_common_fields(self, data):
        """
        Override this method to extract common fields from the data
        """
        return super().extract_common_fields(data)


provider_classes = [ProConnectProvider]
