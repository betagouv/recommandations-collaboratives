from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, ButtonHolder, HTML

"""
Base DSRC form with built-in error handling and autofocus on first error.
"""

class DsrcBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_autofocus_on_first_error()
        self.helper = FormHelper()
        for field_name, field in self.fields.items():
            if isinstance(field, forms.CharField):
                 # If the widget is already a PasswordInput or EmailInput, skip it
                if isinstance(field.widget, (forms.PasswordInput, forms.Textarea)):
                    continue
                field.widget = forms.TextInput(attrs={"classes": "dsrc-input"})
            if isinstance(field, forms.BooleanField):
                field.widget = forms.CheckboxInput(attrs={"classes": "dsrc-checkbox"})
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
        self.helper.form_class = 'dsrc-color-primary'
        self.helper.form_method = 'post'
        self.helper.form_action = 'test_form'

        self.helper.layout = Layout(
            Fieldset(
                'Créez votre compte', # The first argument is the legend of the fieldset
                'sample_text',
                'sample_phone',
                'sample_email',
                'sample_password',
                'sample_postcode',
                'sample_description',
                'sample_boolean',
                'sample_select',
                'sample_disabled_field',
                'sample_radio_group',
                'sample_checkbox_group',
            ),
            ButtonHolder(
                    HTML('<span>Information Saved</span>'),
                    Submit('submit', 'submit'),
                )
        )

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

    sample_password = forms.CharField(
        label="Mot de passe", required=True, widget=forms.PasswordInput(attrs={"classes": "dsrc-input", "size": "sm"})
    )

    sample_postcode = forms.CharField(max_length=5, required=False, label="Code Postal")

    sample_description = forms.CharField(label="Description", widget=forms.Textarea(attrs={"rows":"5", "classes": "dsrc-input"}), required=False)

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

    sample_disabled_field = forms.CharField(
        label="Champ désactivé",
        help_text="Ce champ est désactivé",
        max_length=100,
        disabled=True,
        required=False,
    )

    # Multiple choice Select
    sample_radio_group = forms.ChoiceField(
        label="Boutons radio",
        required=False,
        choices=[(1, "Premier choix unique"), (2, "Second choix unique"), (3, "Troisième choix unique")],
        help_text="Le troisième choix renvoie une erreur s’il est sélectionné",
        widget=forms.RadioSelect(attrs={"classes": "dsrc-radio-group", "size": "sm"}),
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
        widget=forms.CheckboxSelectMultiple(attrs={"classes": "dsrc-checkbox-group", "size": "sm"}),
    )

	# Example clean method
    def clean_sample_radio(self):
        radio_group = self.cleaned_data["sample_radio_group"]

        if radio_group == "3":
            raise forms.ValidationError("Le troisième choix est interdit")

        return radio_group

	# Example clean method
    def clean_sample_checkbox(self):
        checkbox_group = self.cleaned_data["sample_checkbox_group"]

        if checkbox_group == ["3"]:
            raise forms.ValidationError("Le troisième choix est interdit")

        return checkbox_group
# eof
