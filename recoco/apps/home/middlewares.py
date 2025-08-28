from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.shortcuts import redirect, reverse

from recoco.apps.home.models import SiteConfiguration


class RedirectIncompleteProfileUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if not request.user.is_authenticated:
            return self.get_response(request)
        if request.user.profile.needs_profile_update and request.path != reverse(
            "home-update-incomplete-profile"
        ):
            return redirect(reverse("home-update-incomplete-profile"))

        return self.get_response(request)


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
