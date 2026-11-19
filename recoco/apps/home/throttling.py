from rest_framework.throttling import SimpleRateThrottle

from recoco.utils import is_trusted_bot_for_any_site


class UserButExceptionThrottle(SimpleRateThrottle):
    """
    Limits the rate of API calls that may be made by a given user EXCEPT for trusted bots.

    The user id will be used as a unique cache key if the user is
    authenticated.  For anonymous requests, the IP address of the request will be used.
    """

    scope = "user_but_exception"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            if is_trusted_bot_for_any_site(request.user):
                return None  # no throttling for exceptions
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {"scope": self.scope, "ident": ident}
