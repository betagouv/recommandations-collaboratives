"""
Utilities for resources application
"""

from functools import wraps

from django.contrib.auth.views import redirect_to_login


def resources_are_public(request):
    """Return True if resources of the current site can be seen anonymously"""
    site_config = getattr(request, "site_config", None)
    return site_config is None or site_config.public_resources


def public_resources_or_login(view_func):
    """Redirect anonymous visitors to login when resources are not public"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated and not resources_are_public(request):
            return redirect_to_login(request.get_full_path())
        return view_func(request, *args, **kwargs)

    return wrapper


class PublicResourcesOrLoginMixin:
    """Class based view version of `public_resources_or_login`"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not resources_are_public(request):
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)


# eof
