from allauth.account import app_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_username
from django.contrib.sites.models import Site

from . import models


class UVAccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        Fills in a valid username based on email, if required and missing.  If the
        username is already present it is assumed to be valid
        (unique).
        """
        email = user_email(user)

        if app_settings.USER_MODEL_USERNAME_FIELD:
            user_username(user, email)

    def get_from_email(self):
        """
        This is a hook that can be overridden to programatically
        set the 'from' email address for sending emails
        """
        current_site = Site.objects.get_current()
        try:
            site_config = current_site.configuration
        except models.SiteConfiguration.DoesNotExist:
            return super().get_from_email(self)

        return f"{site_config.sender_name} <{site_config.sender_email}>"
