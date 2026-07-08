from datetime import timedelta

import sentry_sdk
from cookie_consent.util import get_cookie_value_from_request
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.utils import timezone
from sesame.middleware import AuthenticationMiddleware as SesameAuthenticationMiddleware
from sesame.utils import get_user

from recoco.apps.home.models import SiteConfiguration, UserProfile


class CurrentSiteConfigurationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if not hasattr(request, "site"):
            raise ImproperlyConfigured(
                "The request object does not have a 'site' attribute. "
                "Ensure that the site middleware is applied before this middleware."
            )

        # TODO: use SiteConfiguration.objects.get() instead of filter().first()
        # Because the site configuration should be unique per site and always exist.
        request.site_config = (
            SiteConfiguration.objects.filter(site=request.site)
            .prefetch_related("onboarding_questions", "crm_available_tags")
            .select_related("project_survey")
            .first()
        )

        return self.get_response(request)


class PreviousActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        now = timezone.now()
        if (
            request.user.is_authenticated
            and not request.user.is_hijacked
            and (
                request.user.profile.previous_activity_at is None
                or request.user.profile.previous_activity_at < now + timedelta(days=1)
            )
        ):
            try:
                # update() rather than save() so that signals are not sent
                UserProfile.objects.filter(user_id=request.user.pk).update(
                    previous_activity_at=now,
                    previous_activity_site=request.site,
                )
            except Exception as e:
                sentry_sdk.capture_exception(e)

        return self.get_response(request)


class SetEnableSesameCookieMiddleware:
    """
    Middleware to set user cookie
    If user is authenticated and there is no cookie, set the cookie,
    If the user is not authenticated and the cookie remains, delete it
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        # if user, cookie consent but no cookie, set cookie
        if (
            request.user.is_authenticated
            and not getattr(request.user, "is_hijacked", True)
            # during hijacking request.user is the hijacked one and is_hijacked is not set
            and get_cookie_value_from_request(request, "preferences", "enable-sesame:")
            and request.COOKIES.get("enable-sesame-user-id", None) != request.user.id
        ):
            current_site = Site.objects.get_current()
            domain = current_site.domain
            response.set_cookie(
                "enable-sesame-user-id",
                request.user.id,
                max_age=timedelta(weeks=52 * 2),  # two years
                domain=domain,
                httponly=True,
                secure=True,
            )
        return response


class SesameWithCookieMiddleware(SesameAuthenticationMiddleware):
    # this code is mainly a copy of sesame's code
    # the difference is meant to check if a cookie exists before actually logging the user in
    def process_request(self, request):
        user = get_user(
            request,
            update_last_login=False if hasattr(request, "session") else None,
        )

        if user is None:
            return None
        if request.user.is_authenticated and request.user.id != user.id:
            return None

        # this cookie is meant to know if user had already signed in
        # on this device, to secure this type of authentication
        cookie_user_id = (
            request.COOKIES.get("enable-sesame-user-id", None)
            if get_cookie_value_from_request(request, "preferences", "enable-sesame:")
            else None
        )
        if cookie_user_id is None:
            return None

        if int(cookie_user_id) != user.id:
            # we don't change the authenticated user. If the previous one does not have access,
            # we rely that the 403 page reminds the user of the authentication status
            return None

        login(request, user)
        # specific tests below comes from sesame original code
        if (
            hasattr(request, "user")
            and request.method == "GET"
            and not self.is_safari(request)
        ):
            return self.get_redirect(request)
