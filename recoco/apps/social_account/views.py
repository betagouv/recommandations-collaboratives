from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal import jwtkit
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.openid_connect.views import (
    OpenIDConnectOAuth2Adapter,
)


class CustomOpenIDConnectOAuth2Adapter(OpenIDConnectOAuth2Adapter):
    @property
    def issuer(self):
        return self.openid_config["issuer"]

    @property
    def jwks_uri(self):
        return self.openid_config["jwks_uri"]

    def complete_login(self, request, app, token: SocialToken, response):
        response = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url, headers={"Authorization": "Bearer " + token.token})
        )
        response.raise_for_status()
        jwt = response.content

        payload = jwtkit.verify_and_decode(
            credential=jwt,
            keys_url=self.jwks_uri,
            issuer=self.issuer,
            audience=app.client_id,
            lookup_kid=jwtkit.lookup_kid_jwk,
        )

        return self.get_provider().sociallogin_from_response(request, payload)


def login(request, provider_id):
    view = OAuth2LoginView.adapter_view(
        CustomOpenIDConnectOAuth2Adapter(request, provider_id)
    )
    return view(request)


def callback(request, provider_id):
    view = OAuth2CallbackView.adapter_view(
        CustomOpenIDConnectOAuth2Adapter(request, provider_id)
    )
    return view(request)
