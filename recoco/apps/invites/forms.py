# encoding: utf-8

"""
Forms for invites application

author  : guillaume.libersat@beta.gouv.fr,raphael.marvie@beta.gouv.fr
created : 2022-04-19 14:16:20 CEST
"""

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from . import models

phone_validator = RegexValidator(
    regex=r"^(\+33|0)[0-9]{9}$",
    message="Format attendu : 0102030405 ou +33102030405.",
)


class InviteForm(forms.ModelForm):
    """Standard form for invitations"""

    class Meta:
        model = models.Invite
        fields = ["email", "message"]


class InviteAcceptForm(forms.Form):
    """Complementary informations when accepting an invitation"""

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    organization = forms.CharField(required=True)
    position = forms.CharField(required=True)
    phone_no = PhoneNumberField(
        required=True,
        label="Numéro de téléphone",
        widget=PhoneNumberInternationalFallbackWidget(),
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        help_text="10 caractères minimum, au moins 1 majuscule et 1 chiffre.",
    )
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error(
                "password_confirm", "Les mots de passe ne correspondent pas."
            )
        return cleaned_data
