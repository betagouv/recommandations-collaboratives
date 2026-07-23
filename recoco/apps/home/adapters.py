from urllib import parse

from allauth.account import adapter as allauth_adapter
from allauth.account import app_settings
from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_username
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.urls import reverse

from . import utils
from .models import AdvisorAccessRequest
from .validators import EmailValidatorForBrevo


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

    def is_login_by_code_required(self, request, **kwargs):
        if settings.DEBUG:
            return False
        return request.user.profile.login_with_code

    def clean_email(self, email: str) -> str:
        # brevo conditions:
        # - Longueur totale de l’adresse ≤ 254 caractères
        # - Partie locale (avant @) ≤ 64 caractères
        # - Domaine valide (chaque label ≤ 63 caractères, caractères autorisés uniquement, pas d’espace, pas de <>, etc.)
        EmailValidatorForBrevo()(email)
        return email

    def get_email_confirmation_url(self, request, emailconfirmation):
        url_str = super().get_email_confirmation_url(request, emailconfirmation)

        # redirect according to context
        url_to_redirect = ""
        match request.resolver_match.view_name:
            #                        setup_user_email(request, crm_user, [])
            case "onboarding-signup":
                url_to_redirect = (
                    reverse(
                        "onboarding-summary",
                        args=(request.session["project_id"],),
                    )
                    if request.session["project_id"]
                    else "/"
                )
            case "account_signup":
                advisor_request = AdvisorAccessRequest.objects.filter(
                    user=request.user, site=request.site
                ).first()
                url_to_redirect = reverse(
                    "advisor-access-request-pending", args=[advisor_request.id]
                )
            case "crm-user-update":
                url_to_redirect = "/"
            case _:  # random login
                url_to_redirect = request.path

        if url_to_redirect:
            url = parse.urlsplit(url_str)
            qs = parse.parse_qs(url.query)
            qs["next"] = url_to_redirect
            qs_str = parse.urlencode(qs)
            parts = (url.scheme, url.netloc, url.path, qs_str, url.fragment)
            url_str = parse.urlunsplit(parts)

        return url_str


def send_confirmation_email(request, user, signup=False):
    email_address = EmailAddress.objects.filter(user=user).first()
    email_address.send_confirmation(request, signup)


def confirm_email(request, user):
    email_address, _ = EmailAddress.objects.get_or_create(user=user, email=user.email)
    UVAccountAdapter().confirm_email(request, email_address)


def is_user_validated(user):
    return EmailAddress.objects.filter(user=user, verified=True).exists()


class VerifiedEmailRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not is_user_validated(request.user):
            send_confirmation_email(request, request.user)
            # same behavior as verified_email_required decorator
            return render(request, "account/verified_email_required.html")
        return super().dispatch(request, *args, **kwargs)
