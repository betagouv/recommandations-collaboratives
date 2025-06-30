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

from recoco.apps.geomatics.models import Department

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
        ].label = "Définissez votre mot de passe (8 caractères minimum)"
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


class AdvisorAccessRequestForm(forms.Form):
    is_select_departments = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[
            forms.ChoiceField(label="Oui", value=True),
            forms.ChoiceField(label="Non", value=False),
        ],
        required=True,
    )

    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        label="Départements",
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    comment = forms.CharField(
        label="Commentaire",
        help_text="Expliquez brièvement pourquoi vous demandez l’accès à ces dossiers et en quoi cela est pertinent pour votre rôle, afin de nous aider à examiner votre demande.",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        departments = cleaned_data.get("departments")

        if not departments:
            raise ValidationError("Veuillez sélectionner au moins un département.")


class SiteCreateForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = [
            "name",
            "subdomain",
            "sender_email",
            "sender_name",
            "contact_form_recipient",
            "legal_address",
        ]

    name = forms.CharField(label="Nom du portail")
    subdomain = forms.CharField(
        label="Sous-domaine recoconseil. Ex: bidule si bidule.recoconseil.fr"
    )
