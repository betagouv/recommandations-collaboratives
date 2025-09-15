import re

from allauth.account import adapter as allauth_adapter
from allauth.account import app_settings
from allauth.account.utils import user_email, user_username
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from magicauth import adapters as magicauth_adapters

from . import utils


class UVAccountAdapter(allauth_adapter.DefaultAccountAdapter):
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
        return utils.get_current_site_sender()

    def save_user(self, request, user, form):
        saved_user = super().save_user(request, user, form)

        # Add the current site so she can access all features
        saved_user.profile.sites.add(get_current_site(request))

        return saved_user

    def clean_password(self, password, user=None):
        """
        Validates a password. You can hook into this if you want to
        restric the allowed password choices.
        """
        if re.match(r"^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{8,}$", password):
            return password
        else:
            raise ValidationError(
                "Votre mot de passe doit comporter au moins 8 caractères, une majuscule et un chiffre."
            )


class UVMagicauthAdapter(magicauth_adapters.DefaultAccountAdapter):
    def get_from_email(self):
        """
        This is a hook that can be overridden to programatically
        set the 'from' email address for sending emails
        """
        return utils.get_current_site_sender()

    def email_unknown_callback(self, request, user_email, form):
        """When an email is unknown, create the User with username and email matching the given
        email address"""
        if not user_email:
            super().email_unknown_callback(request, user_email, form)

        user = auth_models.User.objects.create(username=user_email, email=user_email)
        user.profile.sites.add(get_current_site(request))
