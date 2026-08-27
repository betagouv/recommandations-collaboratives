from rest_framework.permissions import BasePermission

from .models import ServiceAPIKey


class HasServiceAPIKey(BasePermission):
    """Grants access to requests authenticated with a service API key.

    Only meaningful on views opting into `ServiceAPIKeyAllowedMixin`, the
    sole place where key authentication is enabled.
    """

    message = "Cette ressource nécessite une clé d'API de service."

    def has_permission(self, request, view):
        return isinstance(request.auth, ServiceAPIKey)
