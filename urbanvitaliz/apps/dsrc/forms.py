from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

"""
Base DSRC form with built-in error handling and autofocus on first error.
"""

class DsrcBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    def set_autofocus_on_first_error(self):
        """
        Sets the autofocus on the first field with an error message.
        Not included in the __init__ by default because it can cause some side effects on
        non-standard fields/forms.
        """
        for field in self.errors.keys():
            self.fields[field].widget.attrs.update({"autofocus": ""})
            break

"""
Example form that extends DsrcBaseForm.
"""
class DsrcExampleForm(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = 'id-dsrc-example-form'
        self.helper.form_class = 'dsrc-form'
        self.helper.form_method = 'post'
        self.helper.form_action = 'test_form'

        self.helper.add_input(Submit('submit', 'Valider'))

    sample_text = forms.CharField(label="Nom d'usager", initial="", required=True)
    sample_phone = forms.CharField(max_length=16, label="Téléphone", initial="", required=True)
    sample_email =  forms.EmailField(
        label="Courriel",
        help_text="Format attendu : prenom.nom@domaine.fr",
        required=True,
    )

    def clean_email(self):
        """Make sure email is lowercased"""
        email = self.cleaned_data["email"]
        return email.lower()

    sample_postcode = forms.CharField(max_length=5, required=False, label="Code Postal")

    sample_description = forms.CharField(label="Description", widget=forms.Textarea(attrs={"rows":"5"}), required=False)

    sample_password = forms.CharField(
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
    sample_radio = forms.BooleanField(label="Cochez la case", required=False)

    # Basic Select
    sample_select = forms.ChoiceField(
        label="Liste déroulante",
        required=False,
        choices=[(None, "Sélectionner une option"), (1, "Option 1"), (2, "Option 2"), (3, "Option 3")],
    )

    # Multiple choice Select
    sample_radio_group = forms.ChoiceField(
        label="Boutons radio",
        required=False,
        choices=[(1, "Premier choix unique"), (2, "Second choix unique"), (3, "Troisième choix unique")],
        help_text="Le troisième choix renvoie une erreur s’il est sélectionné",
        widget=forms.RadioSelect(attrs={"class": "fr-input dsrc-radio"}),
    )

    # Checkbox group
    sample_checkbox_group = forms.MultipleChoiceField(
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

	# Example clean method
    def clean_sample_radio(self):
        sample_radio = self.cleaned_data["sample_radio_group"]

        if sample_radio == "3":
            raise forms.ValidationError("Le troisième choix est interdit")

        return sample_radio

	# Example clean method
    def clean_sample_checkbox(self):
        sample_checkbox = self.cleaned_data["sample_checkbox_group"]

        if sample_checkbox == ["3"]:
            raise forms.ValidationError("Le troisième choix est interdit")

        return sample_checkbox

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_autofocus_on_first_error()

# eof
