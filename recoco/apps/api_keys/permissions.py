from rest_framework.permissions import BasePermission

from .models import ServiceAPIKey


class IsServiceAPIKey(BasePermission):
    """Allow only requests authenticated with a service API key, hence by a bot.

    has_perm cannot tell a bot from a person: site admins hold every permission
    of their site (see the patched get_user_perms in home.models) and
    superusers hold them all. A view reserved to bots adds this permission in
    front of the one it checks, and its view must accept keys
    (authentication_classes = WITH_SERVICE_API_KEY).
    """

    message = "Seul un compte de service, avec sa clé d'API, peut faire cette action."

    def has_permission(self, request, view):
        return isinstance(request.auth, ServiceAPIKey)
