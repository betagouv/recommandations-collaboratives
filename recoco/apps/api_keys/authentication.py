from rest_framework import authentication, exceptions
from rest_framework.settings import api_settings

from .models import ServiceAPIKey


class ServiceAPIKeyAuthentication(authentication.BaseAuthentication):
    keyword = "Api-Key"

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed("Aucune clé d'API fournie.")

        if len(auth) > 2:
            raise exceptions.AuthenticationFailed(
                "La clé d'API ne doit pas contenir d'espace."
            )

        try:
            key = auth[1].decode()
        except UnicodeError as exc:
            raise exceptions.AuthenticationFailed(
                "La clé d'API contient des caractères invalides."
            ) from exc

        return self.authenticate_key(request, key)

    def authenticate_key(self, request, key):
        try:
            api_key = ServiceAPIKey.objects.get_from_key(key)
        except ServiceAPIKey.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("Clé d'API invalide.") from exc

        if api_key.has_expired:
            raise exceptions.AuthenticationFailed("Clé d'API expirée.")

        if api_key.site_id != request.site.id:
            raise exceptions.AuthenticationFailed("Clé d'API invalide pour ce site.")

        return api_key.user, api_key

    def authenticate_header(self, request):
        return self.keyword


class ServiceAPIKeyAllowedMixin:
    """Opts a view into service API key authentication.

    Key authentication is deliberately kept out of
    DEFAULT_AUTHENTICATION_CLASSES: a view without this mixin cannot be
    reached with an API key.
    """

    authentication_classes = list(api_settings.DEFAULT_AUTHENTICATION_CLASSES) + [
        ServiceAPIKeyAuthentication
    ]
