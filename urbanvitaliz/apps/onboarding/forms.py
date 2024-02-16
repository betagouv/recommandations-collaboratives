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
from urbanvitaliz.apps.dsrc.forms import DsrcBaseForm

from . import models


def set_autofocus_on_first_error(self):
	"""
	Sets the autofocus on the first field with an error message.
	Not included in the __init__ by default because it can cause some side effects on
	non-standard fields/forms.
	"""
	for field in self.errors.keys():
		self.fields[field].widget.attrs.update({"autofocus": ""})
		break

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


class ExperimentFormUsingDsrc(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "id-experiment-dsrc-form" # The form id is used for validation, it must be set and unique in the page
        self.helper.form_class = "dsrc-color-primary" # Theme override classes
        self.helper.form_method = "post"
        self.helper.form_action = "test_form"

        self.helper.layout = Layout(
            Fieldset(
                "Créez votre compte", # The first argument is the legend of the fieldset
                "sample_name",
                # "sample_phone",
                # "sample_email",
                # "sample_password",
                # "sample_postcode",
                # "sample_description",
                # "sample_checkbox",
                # "sample_select",
                # "sample_disabled_field",
                # "sample_radio_group",
                # "sample_checkbox_group",
            ),
        )
    # Example clean method
    def clean_sample_email(self):
        """Make sure email is lowercased"""
        sample_email = self.cleaned_data["sample_email"]
        return sample_email.lower()


	  # Example clean method
    def clean_sample_radio_group(self):
        sample_radio_group = self.cleaned_data["sample_radio_group"]

        if sample_radio_group == "3":
            raise forms.ValidationError("Le troisième choix est interdit")

        return sample_radio_group

	  # Example clean method
    def clean_sample_checkbox_group(self):
        sample_checkbox_group = self.cleaned_data["sample_checkbox_group"]

        if sample_checkbox_group == ["3"]:
            raise forms.ValidationError("Le troisième choix est interdit")

        return sample_checkbox_group

    # Messages used to provide help to the user: overload in your forms to change the messages
    def password_message_group(errors=None):
        return {
			"help_text": "Votre mot de passe doit contenir :",
			"messages": [
				{"text" : "12 caractères minimum", "type" : "info"},
				{"text" : "1 caractère spécial minimum", "type" : "info"},
				{"text" : "1 chiffre minimum", "type" : "info"},
			]
        }
    # Basic text input
    sample_name = forms.CharField(label="Nom d'usager", initial="", required=True)

    # Phone input: input type=text, uses max_length to limit the number of characters
    # TODO: add a phone number validation, pattern / mask
    sample_phone = forms.CharField(max_length=16, label="Téléphone", initial="", required=True)

    # Email input: input type=email
    # TODO: add a phone number validation, pattern / mask
    sample_email =  forms.EmailField(
        label="Courriel",
        help_text="Format attendu : prenom.nom@domaine.fr",
        required=True,
    )

    # Password input, with a password widget, show/hide control, and a help text
    sample_password = forms.CharField(
        label="Mot de passe", required=True, widget=forms.PasswordInput(attrs={"size": "sm", "message_group": password_message_group()})
    )

    # Postal code input: input type=text, uses max_length to limit the number of characters
    # TODO: add a phone number validation, pattern / mask
    sample_postcode = forms.CharField(max_length=5, required=False, label="Code Postal")

    # Long text input: native html textarea
    sample_description = forms.CharField(label="Description", widget=forms.Textarea(attrs={"rows":"5"}), required=False)

    sample_disabled_field = forms.CharField(
        label="Champ désactivé",
        help_text="Ce champ est désactivé",
        max_length=100,
        disabled=True,
        required=False,
    )

    # Boolean choice
    sample_checkbox = forms.BooleanField(label="Cochez la case", required=False, widget=forms.CheckboxInput(attrs={"size": "sm"}))

    # Native html Select
    sample_select = forms.ChoiceField(
        label="Liste déroulante",
        required=False,
        initial=None,
        choices=[('', "Sélectionner une option"), (1, "Option 1"), (2, "Option 2"), (3, "Option 3")],
    )

    # Text input, disabled
    sample_disabled_field = forms.CharField(
        label="Champ désactivé",
        help_text="Ce champ est désactivé",
        max_length=100,
        disabled=True,
        required=False,
    )

    # Unique choice : radio group
    sample_radio_group = forms.ChoiceField(
        label="Boutons radio",
        initial=None,
        required=False,
        choices=[(1, "Premier choix unique"), (2, "Second choix unique"), (3, "Troisième choix unique")],
        help_text="Le troisième choix renvoie une erreur s’il est sélectionné",
        widget=forms.RadioSelect(attrs={"size": "sm"}),
    )

    # Multiple choice : checkbox group
    sample_checkbox_group = forms.MultipleChoiceField(
        label="Cases à cocher",
        initial=None,
        required=False,
        choices=[
            ("1", "Premier choix"),
            ("2", "Second choix"),
            ("3", "Troisième choix"),
        ],
        help_text="Le troisième choix renvoie une erreur s’il est sélectionné",
        widget=forms.CheckboxSelectMultiple(attrs={"size": "sm"}),
    )
# eof