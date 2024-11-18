from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .adapters import CustomOpenIDConnectOAuth2Adapter


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
