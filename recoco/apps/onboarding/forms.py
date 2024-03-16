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
from crispy_forms.layout import Layout, Fieldset
from recoco.apps.dsrc.forms import DsrcBaseForm

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
    location = forms.CharField(label="Adresse", required=False)
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


class ExperimentFormUsingDsrcPart1(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "id-onboarding-form-signup"  # The form id is used for validation, it must be set and unique in the page
        self.helper.form_class = "dsrc-color-primary"  # Theme override classes
        self.helper.form_method = "post"
        self.helper.form_action = "test_form"

        self.helper.layout = Layout(
            Fieldset(
                "Créez votre compte",  # The first argument is the legend of the fieldset
                "first_name",
                "last_name",
                "org_name",
                "role",
                "email",
                "phone",
                "password",
            ),
        )

    # Example clean method
    def clean_email_adress(self):
        """Make sure email is lowercased"""
        email_adress = self.cleaned_data["email_adress"]
        return email_adress.lower()

    # Messages used to provide help to the user: overload in your forms to change the messages
    def password_message_group(errors=None):
        return {
            "help_text": "Votre mot de passe doit contenir :",
            "messages": [
                {"text": "12 caractères minimum", "type": "info"},
                {"text": "1 caractère spécial minimum", "type": "info"},
                {"text": "1 chiffre minimum", "type": "info"},
            ],
        }

    first_name = forms.CharField(label="Prénom", initial="", required=True)
    last_name = forms.CharField(label="Nom", initial="", required=True)
    org_name = forms.CharField(
        label="Nom de votre administration ou de votre entreprise",
        initial="",
        required=True,
    )
    role = forms.CharField(label="Fonction", initial="", required=True)

    # TODO: add an email validation, pattern / mask
    email = forms.EmailField(
        label="Adresse email",
        help_text="Format attendu : prenom.nom@domaine.fr",
        required=True,
        initial="",
    )

    # Password input, with a password widget, show/hide control, and a help text
    password = forms.CharField(
        label="Mot de passe",
        required=True,
        widget=forms.PasswordInput(
            attrs={"size": "sm", "message_group": password_message_group()}
        ),
    )

    # TODO: add a phone number validation, pattern / mask
    phone = forms.CharField(max_length=16, label="Téléphone", initial="", required=True)


class OnboardingSigninForm(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "id-onboarding-form-signin"  # The form id is used for validation, it must be set and unique in the page
        self.helper.form_class = "dsrc-color-primary"  # Theme override classes
        self.helper.form_method = "post"
        self.helper.form_action = "test_form"

        self.helper.layout = Layout(
            Fieldset(
                "Vous avez déjà un compte ? Identifiez-vous !",  # The first argument is the legend of the fieldset
                "email_adress",
                "password",
            ),
        )

    # Example clean method
    def clean_email_adress(self):
        """Make sure email is lowercased"""
        email_adress = self.cleaned_data["email_adress"]
        return email_adress.lower()

    # Messages used to provide help to the user: overload in your forms to change the messages
    def password_message_group(errors=None):
        return {
            "help_text": "Votre mot de passe doit contenir :",
            "messages": [
                {"text": "12 caractères minimum", "type": "info"},
                {"text": "1 caractère spécial minimum", "type": "info"},
                {"text": "1 chiffre minimum", "type": "info"},
            ],
        }

    email_adress = forms.EmailField(
        label="Adresse email",
        help_text="Format attendu : prenom.nom@domaine.fr",
        required=True,
    )

    # Password input, with a password widget, show/hide control, and a help text
    password = forms.CharField(
        label="Mot de passe",
        required=True,
        widget=forms.PasswordInput(
            attrs={"size": "sm", "message_group": password_message_group()}
        ),
    )

    # TODO: add a phone number validation, pattern / mask
    phone_number = forms.CharField(
        max_length=16, label="Téléphone", initial="", required=True
    )


class ExperimentFormUsingDsrcPart2(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "id-onboarding-form-project"  # The form id is used for validation, it must be set and unique in the page
        self.helper.form_class = "dsrc-color-primary"  # Theme override classes
        self.helper.form_method = "post"
        self.helper.form_action = "test_form"
        self.helper.form_tag = False
        self.helper.form_button = False

        self.helper.layout = Layout(
            Fieldset(
                "",  # The first argument is the legend of the fieldset
                "name",
                "location",
                "insee",
                "description",
                "response",
            ),
        )

    # Basic text input
    name = forms.CharField(label="Nom du projet", initial="", required=True)
    location = forms.CharField(label="Commune", initial="", required=True)
    insee = forms.CharField(label="INSEE", initial="", required=True)
    description = forms.CharField(
        label="Contexte du projet",
        widget=forms.Textarea(attrs={"rows": "5"}),
        required=True,
    )
    response = forms.CharField(
        label="Posez vos questions",
        widget=forms.Textarea(attrs={"rows": "5"}),
        required=False,
    )


# eof
