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
        return super().extract_common_fields(data) | {
            "siret": data.get("siret", ""),
            "first_name": data.get("given_name", ""),
            "last_name": data.get("usual_name", ""),
            "phone_no": data.get("phone", ""),
        }

    def get_default_scope(self):
        # https://github.com/numerique-gouv/proconnect-documentation/blob/main/doc_fs/scope-claims.md
        return super().get_default_scope() + [
            "given_name",
            "usual_name",
            "siret",
            "idp_id",
            # TODO: the following ones don't work at the moment
            # "phone",
            # "organizational_unit",
            # "is_service_public",
        ]


provider_classes = [ProConnectProvider]
