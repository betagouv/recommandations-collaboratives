import os

from allauth.account.forms import (
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SignupForm,
)
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.core.exceptions import ValidationError


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

        self.fields["password1"].label = (
            "Définissez votre mot de passe (8 caractères minimum)"
        )
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )


class UVLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(UVLoginForm, self).__init__(*args, **kwargs)
        self.fields["login"].widget = forms.TextInput(
            attrs={"type": "email", "class": "fr-input fr-mt-2v fr-mb-4v"}
        )
        self.fields["password"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
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
        self.fields["password1"].label = "Nouveau mot de passe (8 caractères minimum)"
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

    def __init__(self, user, *args, **kwargs):
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
