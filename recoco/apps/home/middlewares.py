from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest

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

        request.site_config = (
            SiteConfiguration.objects.filter(site=request.site)
            .prefetch_related("onboarding_questions", "crm_available_tags")
            .select_related("project_survey")
            .first()
        )

        return self.get_response(request)
