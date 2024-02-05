

import os

from django import forms

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Skip captcha during tests
        if "PYTEST_CURRENT_TEST" in os.environ:
            self.fields.pop("captcha")

    first_name = forms.CharField(label="Prénom du contact", initial="", required=True)
    last_name = forms.CharField(label="Nom du contact", initial="", required=True)
    phone = forms.CharField(max_length=16, label="Téléphone", initial="", required=True)
    email =  forms.EmailField(
        label="Courriel",
        help_text="Format attendu : prenom.nom@domaine.fr",
        required=True,
    )

    def clean_email(self):
        """Make sure email is lowercased"""
        email = self.cleaned_data["email"]
        return email.lower()


    org_name = forms.CharField(
        label="Nom de votre structure", initial="", required=True
    )

    # basic fields

    location = forms.CharField(label="Adresse", required=False)
    postcode = forms.CharField(max_length=5, required=False, label="Code Postal")

    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={"rows":"5"}), required=False)

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
        choices=[(1, "Premier choix unique"), (2, "Second choix unique"), (3, "Troisième choix unique")],
        help_text="Le troisième choix renvoie une erreur s’il est sélectionné",
        widget=forms.RadioSelect(attrs={"class": "fr-input dsrc-radio"}),
    )

    # Checkbox group
    sample_checkbox = forms.MultipleChoiceField(
        label="Cases à cocher",
        required=False,
        choices=[
            ("1", "Premier choix"),
            ("2", "Second choix"),
            ("3", "Troisième choix"),
        ],
        help_text="Le troisième choix renvoie une erreur s’il est sélectionné",
        widget=forms.CheckboxSelectMultiple(attrs={"class": "fr-input dsrc-checkbox"}),
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

        if sample_checkbox == ["3"]:
            raise forms.ValidationError("Le troisième choix est interdit")

        return sample_checkbox

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_autofocus_on_first_error()

# eof
