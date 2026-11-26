from datetime import timedelta

from django.contrib.auth.models import update_last_login
from django.utils import timezone
from rest_framework import authentication, exceptions
from rest_framework.settings import api_settings

from .models import ServiceAPIKey


class ServiceAPIKeyAuthentication(authentication.BaseAuthentication):
    keyword = "Api-Key"
    invalid_key_message = "Clé d'API invalide, expirée ou non-autorisée pour ce site."

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
            raise exceptions.AuthenticationFailed(self.invalid_key_message) from exc

        if api_key.has_expired or api_key.site_id != request.site.id:
            raise exceptions.AuthenticationFailed(self.invalid_key_message)

        user = api_key.user
        # mirror a regular login, at most once per hour to avoid a write per request
        if not user.last_login or user.last_login < timezone.now() - timedelta(hours=1):
            update_last_login(None, user)

        return user, api_key

    def authenticate_header(self, request):
        return self.keyword


# Login methods for a view that service API keys may reach.
# The Key login is kept out of DEFAULT_AUTHENTICATION_CLASSES.
# Views that accepts this method needs to declare it
#   class MyView(APIView):
#       authentication_classes = WITH_SERVICE_API_KEY
#
#   @api_view(["GET"])
#   @authentication_classes(WITH_SERVICE_API_KEY)
#   def my_view(request): ...
WITH_SERVICE_API_KEY = [
    *api_settings.DEFAULT_AUTHENTICATION_CLASSES,
    ServiceAPIKeyAuthentication,
]
