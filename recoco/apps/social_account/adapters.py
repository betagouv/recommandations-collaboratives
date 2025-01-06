from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, get_adapter
from allauth.socialaccount.internal import jwtkit
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.openid_connect.views import (
    OpenIDConnectOAuth2Adapter,
)
from django.utils.crypto import get_random_string


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def generate_state_param(self, state: dict) -> str:
        return get_random_string(32)

    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.
        """
        user = super().populate_user(request, sociallogin, data)

        # TODO: compléter les informations de l'utilisateur si possible
        # https://github.com/numerique-gouv/proconnect-documentation/blob/main/doc_fs/donnees_fournies.md
        # user.organization = ...
        # user.organization_position = ...
        # user.siret = ...

        if "phone_number" in data:
            user.phone_no = data.get("phone_number")

        return user

    def pre_social_login(self, request, sociallogin) -> None:
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        You can use this hook to intervene, e.g. abort the login by
        raising an ImmediateHttpResponse
        """
        return super().pre_social_login(request, sociallogin)

    def is_open_for_signup(self, request, sociallogin) -> bool:
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        return super().is_open_for_signup(request, sociallogin)


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
