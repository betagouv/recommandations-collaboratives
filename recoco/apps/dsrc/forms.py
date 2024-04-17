from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset


"""
Base DSRC form:
- built-in error handling
- autofocus on first error
- dsrc classes for form elements
"""


class DsrcBaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        # If the widget is already set for a Field: merge the default `dsrc` attrs with the ones provided by the widget
        for field_name, field in self.fields.items():
            if isinstance(field, forms.CharField):
                if isinstance(
                    field.widget,
                    (forms.Textarea, forms.PasswordInput, forms.EmailInput),
                ):
                    # If the widget is already a Textarea
                    field.widget.attrs = field.widget.attrs | {"classes": "dsrc-input"}
                elif isinstance(field, forms.TextInput):
                    field.widget = forms.TextInput(attrs={"classes": "dsrc-input"})
            if isinstance(field, forms.BooleanField):
                # If the widget is already a CheckboxInput
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs = field.widget.attrs | {
                        "classes": "dsrc-checkbox-group"
                    }
            if isinstance(field, forms.ChoiceField):
                # If the widget is already a RadioSelect
                if isinstance(field.widget, forms.RadioSelect):
                    field.widget.attrs = field.widget.attrs | {
                        "classes": "dsrc-radio-group"
                    }
                # If the widget is already a CheckboxSelectMultiple
                elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                    field.widget.attrs = field.widget.attrs | {
                        "classes": "dsrc-checkbox-group"
                    }
                # Default: set a Select widget with dsrc classes
                else:
                    field.widget = forms.Select(attrs={"classes": "dsrc-select"})

            # Add selector patterns used in Cypress tests
            field.widget.attrs = field.widget.attrs | {
                "field_test_id": f"dsrc_test_{field_name}_field",
                "input_test_id": f"dsrc_test_{field_name}_input",
            }
            # Set placeholders
            field.widget.attrs = field.widget.attrs | {
                "placeholder": field.initial if field.label is None else ""
            }
            field.error_messages = field.error_messages | {
                "required": "Texte d’erreur obligatoire",
                "invalid": "Texte de validation",
            }

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
- Uses crispy_forms for managing the layout and fields rendering
- To use this form, you can include the tag in your template:
    {% crispy dsrc_example_form %}
- You can see an example of this form integrated:
    - in a template here: './templates/dsrc/samples/page_form.html'
    - in a view here: './views.py'
- Once you have started the application, you can access the form at the following URL:
	http://subdomain.localhost:8000/dsrc_form
"""


class DsrcExampleForm(DsrcBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = "id-dsrc-example-form"  # The form id is used for validation, it must be set and unique in the page
        self.helper.form_class = "dsrc-color-primary"  # Theme override classes
        self.helper.form_method = "post"
        self.helper.form_action = "test_form"

        self.helper.layout = Layout(
            Fieldset(
                "Créez votre compte",  # The first argument is the legend of the fieldset
                "sample_name",
                "sample_phone",
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
                {"text": "12 caractères minimum", "type": "info"},
                {"text": "1 caractère spécial minimum", "type": "info"},
                {"text": "1 chiffre minimum", "type": "info"},
            ],
        }

    # Basic text input
    sample_name = forms.CharField(label="Nom d'usager", initial="", required=True)

    # Phone input: input type=text, uses max_length to limit the number of characters
    # TODO: add a phone number validation, pattern / mask
    sample_phone = forms.CharField(
        max_length=16, label="Téléphone", initial="", required=True
    )

    # Email input: input type=email
    # TODO: add a phone number validation, pattern / mask
    sample_email = forms.EmailField(
        label="Courriel",
        help_text="Format attendu : prenom.nom@domaine.fr",
        required=True,
    )

    # Password input, with a password widget, show/hide control, and a help text
    sample_password = forms.CharField(
        label="Mot de passe",
        required=True,
        widget=forms.PasswordInput(
            attrs={"size": "sm", "message_group": password_message_group()}
        ),
    )

    # Postal code input: input type=text, uses max_length to limit the number of characters
    # TODO: add a phone number validation, pattern / mask
    sample_postcode = forms.CharField(max_length=5, required=False, label="Code Postal")

    # Long text input: native html textarea
    sample_description = forms.CharField(
        label="Description", widget=forms.Textarea(attrs={"rows": "5"}), required=False
    )

    sample_disabled_field = forms.CharField(
        label="Champ désactivé",
        help_text="Ce champ est désactivé",
        max_length=100,
        disabled=True,
        required=False,
    )

    # Boolean choice
    sample_checkbox = forms.BooleanField(
        label="Cochez la case",
        required=False,
        widget=forms.CheckboxInput(attrs={"size": "sm"}),
    )

    # Native html Select
    sample_select = forms.ChoiceField(
        label="Liste déroulante",
        required=False,
        initial=None,
        choices=[
            ("", "Sélectionner une option"),
            (1, "Option 1"),
            (2, "Option 2"),
            (3, "Option 3"),
        ],
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
        choices=[
            (1, "Premier choix unique"),
            (2, "Second choix unique"),
            (3, "Troisième choix unique"),
        ],
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
