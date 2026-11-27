from urllib import parse

from allauth.account import adapter as allauth_adapter
from allauth.account import app_settings
from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_username
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

from . import utils
from .config import (
    EMAIL_CONFIRMATION_FLOW_SESSION_KEY,
    EMAIL_CONFIRMED_BY_LOGIN_CODE_ATTR,
    SIGNUP_USER_ID_SESSION_KEY,
)
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

    def is_login_by_code_required(self, login):
        if settings.DEBUG:
            return False
        if not login.user or login.user.is_anonymous:
            # fallback for cases with login started as a way to prevent enumeration by allauth
            return False
        if login.signal_kwargs and login.signal_kwargs.get("sociallogin"):
            return False
        return login.user.profile.login_with_code

    def get_login_stages(self) -> list[str]:
        # custom MFA conditions
        return [
            "recoco.apps.home.stages.RecocoMFAAuthenticateStage"
            if stage == "allauth.mfa.stages.AuthenticateStage"
            else stage
            for stage in super().get_login_stages()
        ]

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
        match request.session.get(EMAIL_CONFIRMATION_FLOW_SESSION_KEY, None):
            case "onboarding":
                url_to_redirect = (
                    reverse(
                        "onboarding-summary",
                        args=(request.session["project_id"],),
                    )
                    if "project_id" in request.session
                    else "/"
                )
            case "advisor":
                url_to_redirect = reverse("advisor-access-request-pending")
            case _:
                # the email confirmation was sent because an admin changed the user's email
                if request.resolver_match.view_name == "crm-user-update":
                    url_to_redirect = "/"
                else:  # random login
                    url_to_redirect = request.path

        if url_to_redirect:
            url = parse.urlsplit(url_str)
            qs = parse.parse_qs(url.query)
            qs["next"] = url_to_redirect
            qs_str = parse.urlencode(qs)
            parts = (url.scheme, url.netloc, url.path, qs_str, url.fragment)
            url_str = parse.urlunsplit(parts)

        return url_str

    def pre_login(
        self,
        request,
        user,
        *,
        email_verification,
        signal_kwargs,
        email,
        signup,
        redirect_url,
    ):
        # this is to easily skip to controlled second step signup form.
        # might be cleaner through a custom login stage conditionned by signup arg
        if redirect_url == reverse_lazy("advisor-access-request"):
            return redirect(redirect_url)
        if request.resolver_match.url_name == "account_confirm_login_code":
            if getattr(request, EMAIL_CONFIRMED_BY_LOGIN_CODE_ATTR, False):
                # flag set on email confirmation if it was done by allauth on a login by code so the account was never used before and password is deemed usafe
                invalidate_password(user)
            reset_session_to_validate_if_needed(user, request)
        if not user.is_active:
            return self.respond_user_inactive(request, user)

    def respond_email_verification_sent(self, request, user):
        if user:
            request.session[SIGNUP_USER_ID_SESSION_KEY] = user.id
        return super().respond_email_verification_sent(request, user)


def send_confirmation_email(request, user, signup=False):
    email_address = EmailAddress.objects.filter(user=user).first()
    email_address.send_confirmation(request, signup)


def confirm_email(request, user):
    email_address, _ = EmailAddress.objects.get_or_create(user=user, email=user.email)
    UVAccountAdapter().confirm_email(request, email_address)


def reset_session_to_validate_if_needed(user, request):
    if EmailAddress.objects.filter(
        user=user, email=user.email, verified=True
    ).exists():  # address is valid
        return
    invalidate_password(user)

    confirm_email(request, user)


def invalidate_password(user):
    user.set_unusable_password()
    # persist it: confirm_email does not always save the user
    user.save(update_fields=["password"])
    # this resets all session
    # cf https://docs.djangoproject.com/en/5.2/topics/auth/default/#session-invalidation-on-password-change
