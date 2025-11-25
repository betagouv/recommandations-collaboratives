# encoding: utf-8

"""
Forms for onboarding application

author  : guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created : 2022-06-06 14:16:20 CEST
"""

import os

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from crispy_forms.layout import Fieldset, Layout
from django import forms
from django.urls import reverse

from recoco.apps.dsrc.forms import DsrcBaseForm


##################################################
# Onboarding multi-step forms
##################################################
class OnboardingSignupForm(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "id-onboarding-signup-form"  # The form id is used for validation, it must be set and unique in the page
        self.helper.form_method = "post"
        self.helper.action_button = {"submit": {"label": "Suivant"}}
        self.helper.form_tag = False
        self.helper.form_button = False

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
    def clean_email(self):
        """Make sure email is lowercased"""
        email = self.cleaned_data["email"]
        return email.lower()

    # Messages used to provide help to the user: overload in your forms to change the messages
    def password_message_group(errors=None):
        return {
            "help_text": "Votre mot de passe doit contenir :",
            "messages": [
                {
                    "text": "(10 caractères minimum et au moins 1 majuscule et 1 chiffre)",
                    "type": "info",
                }
            ],
        }

    first_name = forms.CharField(label="Prénom *", initial="", required=True)
    last_name = forms.CharField(label="Nom *", initial="", required=True)
    org_name = forms.CharField(
        label="Nom de votre organisation *",
        help_text="Si vous êtes un particulier, indiquez votre nom. Votre administration, entreprise, association. Si vous êtes un particulier, écrivez 'Particulier'.",
        initial="",
    )
    role = forms.CharField(label="Fonction *", initial="", required=True)

    # TODO: add an email validation, pattern / mask
    email = forms.EmailField(
        label="Adresse email *",
        help_text="Format attendu : prenom.nom@domaine.fr",
        required=True,
        disabled=True,
    )

    # Password input, with a password widget, show/hide control, and a help text
    password = forms.CharField(
        label="Mot de passe *",
        required=True,
        help_text="Votre mot de passe doit contenir 10 caractères minimum et au moins 1 majuscule et 1 chiffre",
        widget=forms.PasswordInput(
            attrs={"size": "sm", "message_group": password_message_group()}
        ),
    )

    # TODO: add a phone number validation, pattern / mask
    phone = forms.CharField(
        max_length=16,
        label="Numéro de téléphone *",
        initial="",
        help_text="Votre numéro de téléphone ne sera jamais diffusé en dehors du site. Il permet aux administrateurs ou aux partenaires de votre dossier de vous joindre plus facilement. Format attendu: 0102030405.",
        required=True,
    )


class OnboardingProject(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "id-onboarding-project-form"  # The form id is used for validation, it must be set and unique in the page
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.form_button = False
        self.helper.action_button = {
            "submit": {
                "label": "Suivant",
            }
        }

        self.helper.layout = Layout(
            Fieldset(
                "Créez votre dossier",  # The first argument is the legend of the fieldset
                "name",
                "location",
                "postcode",
                "insee",
                "description",
                "email",
                "captcha",
            )
        )

        # Skip captcha during tests
        if "PYTEST_CURRENT_TEST" in os.environ:
            self.fields.pop("captcha")

    name = forms.CharField(
        label="Nom de votre dossier *",
        initial="",
        required=True,
        help_text="Donnez un nom court pour désigner le dossier ou le projet. Inutile d'ajouter le nom de la commune ou l'adresse.",
    )
    location = forms.CharField(
        label="Adresse",
        initial="",
        required=False,
        help_text="Indiquez une adresse ou une indication pour localiser le lieu, ou laissez vide si ça n'est pas applicable.",
    )
    postcode = forms.CharField(label="Code postal *", initial="", required=True)

    insee = forms.CharField(
        max_length=5,
        label="Commune",
        required=True,
    )

    description = forms.CharField(
        label="Résumé de votre demande *",
        initial="",
        required=True,
        help_text="Décrivez votre demande ou dossier et son contexte en quelques mots.",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    email = forms.EmailField(
        label="Adresse email *",
        required=True,
        help_text="Format attendu : prenom.nom@domaine.fr",
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(api_params={"hl": "fr"}))


class PrefillSetuserForm(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "id-prefill-setuser-form"  # The form id is used for validation, it must be set and unique in the page
        self.helper.form_method = "post"
        self.helper.action_button = {"submit": {"label": "Suivant"}}
        self.helper.form_tag = False
        self.helper.form_button = False

        self.helper.layout = Layout(
            Fieldset(
                "Pour qui remplissez-vous ce dossier",  # The first argument is the legend of the fieldset
                "first_name",
                "last_name",
                "org_name",
                "role",
                "email",
                "phone",
            ),
        )

    def clean_email(self):
        """Make sure email is lowercased"""
        email = self.cleaned_data["email"]
        return email.lower()

    first_name = forms.CharField(
        label="Prénom du référent *", initial="", required=True
    )
    last_name = forms.CharField(label="Nom du référent *", initial="", required=True)
    org_name = forms.CharField(
        label="Organisation du référent *",
        help_text="Collectivité, administration, entreprise, association...",
        initial="",
    )
    role = forms.CharField(label="Fonction du référent *", initial="", required=True)

    # TODO: add an email validation, pattern / mask
    email = forms.EmailField(
        label="Adresse email du référent *",
        help_text="Format attendu : prenom.nom@domaine.fr",
        required=True,
        initial="",
    )

    # TODO: add a phone number validation, pattern / mask
    phone = forms.CharField(
        max_length=16,
        label="Téléphone du référent *",
        initial="",
        help_text="Format attendu: 0102030405",
        required=True,
    )

    message = forms.CharField(
        label="Message personnalisé au référent, accompagnant l'invitation à rejoindre le dossier",
        initial="",
        required=False,
        help_text="Ce message sera envoyé au référent par mail. Il est facultatif.",
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class PrefillProjectForm(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "id-prefill-project-form"  # The form id is used for validation, it must be set and unique in the page
        self.helper.form_method = "post"
        self.helper.form_tag = False
        self.helper.form_button = False
        self.helper.action_button = {
            "submit": {
                "label": "Suivant",
            },
            "cancel": {
                "label": "Précédent",
                "href": reverse("onboarding-prefill-set-user"),
            },
        }

        self.helper.layout = Layout(
            Fieldset(
                "",  # The first argument is the legend of the fieldset
                "name",
                "location",
                "postcode",
                "insee",
                "description",
            )
        )

    name = forms.CharField(
        label="Nom de votre dossier *",
        initial="",
        required=True,
        help_text="Donnez un nom court pour désigner le dossier ou le projet. Inutile d'ajouter le nom de la commune ou l'adresse.",
    )
    location = forms.CharField(
        label="Adresse",
        initial="",
        required=False,
        help_text="Indiquez une adresse ou une indication pour localiser le lieu, ou laissez vide si ça n'est pas applicable.",
    )
    postcode = forms.CharField(label="Code postal", initial="", required=True)

    insee = forms.CharField(
        max_length=5,
        label="Commune",
        required=True,
    )

    description = forms.CharField(
        label="Résumé de votre demande *",
        initial="",
        required=True,
        help_text="Décrivez votre dossier et son contexte en quelques mots.",
        widget=forms.Textarea(attrs={"rows": 3}),
    )


# eof
