# encoding: utf-8

"""
Forms for onboarding application

author  : guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created : 2022-06-06 14:16:20 CEST
"""

import os

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms

from . import models


##################################################
# Notes
##################################################
class OnboardingResponseForm(forms.ModelForm):
    class Meta:
        model = models.OnboardingResponse
        fields = [
            "first_name",
            "last_name",
            "phone",
            "org_name",
            "email",
            "name",
            "location",
            "insee",
            "description",
            "response",
        ]

    first_name = forms.CharField(label="Prénom du contact", initial="", required=True)
    last_name = forms.CharField(label="Nom du contact", initial="", required=True)
    phone = forms.CharField(max_length=16, label="Téléphone", initial="", required=True)
    email = forms.CharField(label="Courriel", required=True)

    def clean_email(self):
        """Make sure email is lowercased"""
        email = self.cleaned_data["email"]
        return email.lower()

    org_name = forms.CharField(
        label="Nom de votre structure", initial="", required=True
    )

    name = forms.CharField(label="Nom du projet", max_length=128, required=True)
    location = forms.CharField(label="Adresse", required=True)
    postcode = forms.CharField(max_length=5, required=False, label="Code Postal")
    insee = forms.CharField(max_length=5, required=False, label="Code Insee")

    description = forms.CharField(label="Description")


class OnboardingResponseWithCaptchaForm(OnboardingResponseForm):
    class Meta:
        model = models.OnboardingResponse
        fields = [
            "first_name",
            "last_name",
            "phone",
            "org_name",
            "email",
            "name",
            "location",
            "insee",
            "description",
            "response",
            "captcha",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Skip captcha during tests
        if "PYTEST_CURRENT_TEST" in os.environ:
            self.fields.pop("captcha")

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(api_params={"hl": "fr"}))


class SelectCommuneForm(forms.Form):
    def __init__(self, communes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commune"] = forms.ModelChoiceField(
            queryset=communes, widget=forms.RadioSelect, label="Votre commune :"
        )


# eof
