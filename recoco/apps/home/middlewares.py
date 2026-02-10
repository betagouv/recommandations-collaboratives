from datetime import timedelta

import sentry_sdk
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.utils import timezone

from recoco.apps.home.models import SiteConfiguration


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
                request.user.profile.previous_activity_at = now
                request.user.profile.previous_activity_site = request.site
                request.user.profile.save()
            except Exception as e:
                sentry_sdk.capture_exception(e)

        return self.get_response(request)
