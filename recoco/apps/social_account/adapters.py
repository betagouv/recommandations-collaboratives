from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, get_adapter
from allauth.socialaccount.internal import jwtkit
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.openid_connect.views import (
    OpenIDConnectOAuth2Adapter,
)
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from recoco.apps.home.adapters import confirm_email


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def generate_state_param(self, state: dict) -> str:
        return get_random_string(32)

    def pre_social_login(self, request, sociallogin) -> None:
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        (and before the pre_social_login signal is emitted).

        You can use this hook to intervene, e.g. abort the login by
        raising an ImmediateHttpResponse
        """

        def reset_session_to_validate_if_needed(user, request):
            if EmailAddress.objects.filter(
                email=user.email, verified=True
            ).exists():  # address is valid
                return

            user.set_unusable_password()
            # this resets all session
            # cf https://docs.djangoproject.com/en/5.2/topics/auth/default/#session-invalidation-on-password-change

            confirm_email(request, user)

        user = sociallogin.user
        try:
            user = User.objects.get(email=user.email)
            reset_session_to_validate_if_needed(user, request)
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def get_signup_form_initial_data(self, sociallogin):
        return super().get_signup_form_initial_data(sociallogin) | {
            "phone_no": sociallogin.account.extra_data.get("phone_number", ""),
            # TODO: add siret to signup form
            # "siret": sociallogin.account.extra_data.get("siret", ""),
        }


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
