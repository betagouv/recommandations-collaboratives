import os

from allauth.account.forms import (
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SignupForm,
)
from allauth.mfa.models import Authenticator
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse

from recoco.apps.geomatics.models import Department

from .config import SIGNUP_USER_ID_SESSION_KEY
from .models import SiteConfiguration


class UVSignupForm(SignupForm):
    field_order = [
        "first_name",
        "last_name",
        "organization",
        "organization_position",
        "email",
        "phone_no",
        "password1",
        "password2",
        "captcha",
    ]

    def __init__(self, *args, **kwargs):
        super(UVSignupForm, self).__init__(*args, **kwargs)

        self.fields[
            "password1"
        ].label = "Définissez votre mot de passe (10 caractères minimum et au moins 1 majuscule et 1 chiffre)"
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )

    def custom_signup(self, request, user):
        super().custom_signup(request, user)
        # sets up session data to prefill advisor access request form
        request.session[SIGNUP_USER_ID_SESSION_KEY] = user.pk

    def try_save(self, request):
        # we finish access request for this site after user login so we need to setup session
        if self.account_already_exists:
            user = User.objects.get(email=self.cleaned_data.get("email"))
            if not user.profile.sites.filter(id=request.site.id).exists():
                next_url = reverse("advisor-access-request")
                login = reverse("account_login")
                url = f"{login}?next={next_url}"
                resp = redirect(url)
                request.session[SIGNUP_USER_ID_SESSION_KEY] = user.pk
                return user, resp
            # else case handled in parent try_save

        return super().try_save(request)


class UVLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(UVLoginForm, self).__init__(*args, **kwargs)
        self.fields["login"].widget = forms.TextInput(
            attrs={"type": "email", "class": "fr-input fr-mt-2v fr-mb-5v"}
        )
        self.fields["password"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-5v"}
        )


class UVResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(UVResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget = forms.TextInput(
            attrs={"type": "email", "class": "fr-input fr-mt-2v fr-mb-4v"}
        )


class UVResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(UVResetPasswordKeyForm, self).__init__(*args, **kwargs)
        self.fields[
            "password1"
        ].label = "Nouveau mot de passe (10 caractères minimum et au moins 1 majuscule et 1 chiffre)"
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )

        self.fields["password2"].label = "Nouveau mot de passe (confirmation)"
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=256)
    content = forms.CharField(max_length=2048, widget=forms.Textarea)
    name = forms.CharField(max_length=128)
    email = forms.CharField(max_length=128)

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(api_params={"hl": "fr"}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        if user.is_authenticated:
            del self.fields["name"]
            del self.fields["email"]

        # Prevent tests from failing
        if "PYTEST_CURRENT_TEST" in os.environ:
            self.fields.pop("captcha")


class UserPasswordFirstTimeSetupForm(forms.Form):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={"class": "form-control fr-py-2v fr-mt-2v fr-mb-4v"}
        ),
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(
            attrs={"class": "form-control fr-py-2v fr-mt-2v fr-mb-4v"}
        ),
    )
    next = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Les mots de passe ne correspondent pas.")


class AdvisorAccessRequestForm(forms.Form):
    advisor_access_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[
            ("National", "Toute la France"),
            ("Regional", "Un ou plusieurs départements spécifiques"),
        ],
        required=True,
        label="Sélection du territoire",
    )

    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        label="Départements",
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    comment = forms.CharField(
        label="Commentaire",
        help_text="Expliquez brièvement pourquoi vous demandez l'accès à ces dossiers et en quoi cela est pertinent pour votre rôle, afin de nous aider à examiner votre demande.",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        advisor_access_type = cleaned_data.get("advisor_access_type")
        departments = cleaned_data.get("departments")
        if advisor_access_type == "Regional" and not departments:
            self.add_error(
                "departments", "Merci de sélectionner au moins un département."
            )
        return cleaned_data


class SiteCreateForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = [
            "name",
            "subdomain",
            "sender_name",
            "contact_form_recipient",
            "legal_address",
        ]

    name = forms.CharField(label="Nom du portail")
    subdomain = forms.CharField(
        label="Sous-domaine recoconseil. Ex: bidule si bidule.recoconseil.fr"
    )


class TwoFaConfigForm(forms.Form):
    two_fa_mode = forms.ChoiceField(
        label="Quelle double authentification",
        help_text="La double authentification par application externe est plus sécurisée",
        choices=[
            ("totp", "Application externe"),
            ("login_with_code", "Envoi d'un code par mail"),
            ("none", "Aucun"),
        ],
        widget=forms.RadioSelect,
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user.is_authenticated and user.profile.requires_2fa:
            self.fields["two_fa_mode"].choices = [
                c for c in self.fields["two_fa_mode"].choices if c[0] != "none"
            ]
        if user.profile.login_with_code:
            self.fields["two_fa_mode"].initial = "login_with_code"
        if Authenticator.objects.filter(
            type=Authenticator.Type.TOTP, user=user
        ).exists():
            self.fields["two_fa_mode"].initial = "totp"

    def clean(self):
        cleaned_data = super().clean()
        if (
            self.user.is_authenticated
            and self.user.profile.requires_2fa
            and self.data.get("two_fa_mode") == "none"
        ):
            self.add_error(
                "two_fa_mode", "Sélectionnez un mode de double authentification"
            )
        return cleaned_data
