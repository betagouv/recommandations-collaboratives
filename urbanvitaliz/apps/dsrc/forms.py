

import os

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms

from . import models

from django import forms

class DsrcBaseForm(forms.Form):
    """
    A base form
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_autofocus_on_first_error(self):
        """
        Sets the autofocus on the first field with an error message.
        Not included in the __init__ by default because it can cause some side effects on
        non-standard fields/forms.
        """
        for field in self.errors.keys():
            self.fields[field].widget.attrs.update({"autofocus": ""})
            break

class DsrcExampleForm(DsrcBaseForm):
    
    class Meta:
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
    # basic fields
    user_name = forms.CharField(label="Nom d’utilisateur", max_length=100)

    user_email = forms.EmailField(
        label="Adresse électronique",
        help_text="Format attendu : prenom.nom@domaine.fr",
        required=True,
    )

    password = forms.CharField(
        label="Mot de passe", required=True, widget=forms.PasswordInput
    )

    sample_disabled_field = forms.CharField(
        label="Champ désactivé",
        help_text="Ce champ est désactivé",
        max_length=100,
        disabled=True,
        required=False,
    )

    # Booleans and choicefields
    sample_boolean = forms.BooleanField(label="Cochez la case", required=False)

    # Basic Select
    sample_select = forms.ChoiceField(
        label="Liste déroulante",
        required=False,
        choices=[(None, "Sélectionner une option"), (1, "Option 1"), (2, "Option 2"), (3, "Option 3")],
    )

    # Multiple choice Select
    sample_radio = forms.ChoiceField(
        label="Boutons radio",
        required=False,
        choices=[(1, "Premier choix"), (2, "Second choix"), (3, "Troisième choix")],
        help_text="Le troisième choix renvoie une erreur s’il est sélectionné",
        widget=forms.RadioSelect,
    )

    # Checkbox group
    sample_checkbox = forms.ChoiceField(
        label="Cases à cocher",
        required=False,
        choices=[
            ("1", "Premier choix"),
            ("2", "Second choix"),
            ("3", "Troisième choix"),
        ],
        help_text="Le troisième choix renvoie une erreur s’il est sélectionné",
        widget=forms.CheckboxSelectMultiple,
    )

    # Simple text blocks
    description = forms.CharField(widget=forms.Textarea, required=False)

    def clean_sample_radio(self):
        sample_radio = self.cleaned_data["sample_radio"]

        if sample_radio == "3":
            raise forms.ValidationError("Le troisième choix est interdit")

        return sample_radio

    def clean_sample_checkbox(self):
        sample_checkbox = self.cleaned_data["sample_checkbox"]

        if sample_checkbox == ["2"]:
            raise forms.ValidationError("Le troisième choix est interdit")

        return sample_checkbox

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_autofocus_on_first_error()

class SelectCommuneForm(forms.Form):
    def __init__(self, communes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commune"] = forms.ModelChoiceField(
            queryset=communes, widget=forms.RadioSelect, label="Votre commune :"
        )

# eof
