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


provider_classes = [ProConnectProvider]
