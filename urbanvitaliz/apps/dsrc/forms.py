

import os

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms

from . import models

from django import forms

class DsrcBaseForm(forms.Form):
    """
    A base form that adds the necessary class on relevant fields
    """

    # These input widgets don't need the fr-input class
    WIDGETS_NO_FR_INPUT = [
        forms.widgets.CheckboxInput,
        forms.widgets.FileInput,
        forms.widgets.ClearableFileInput,
    ]

    # @property
    # def default_renderer(self):
    #     from django.conf import settings, global_settings
   
    #     return (
    #         DsrcDjangoTemplates  # Settings wasn't modified
    #         if settings.FORM_RENDERER == global_settings.FORM_RENDERER
    #         else get_default_renderer()
    #     )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            """
            Depending on the widget, we have to add some classes:
            - on the outer group
            - on the form field itsef

            If a class is already set, we don't force the Dsrc-specific classes.
            """
            print()
            if "class" not in visible.field.widget.attrs:
                if type(visible.field.widget) in [
                    forms.widgets.Select,
                    forms.widgets.SelectMultiple,
                ]:
                    visible.field.widget.attrs["class"] = "fr-select"
                    visible.field.widget.group_class = "fr-select-group"
                elif type(visible.field.widget) == forms.widgets.RadioSelect:
                    visible.field.widget.attrs["dsrc"] = "dsrc"
                    visible.field.widget.group_class = "fr-radio-group"
                elif type(visible.field.widget) == forms.widgets.CheckboxSelectMultiple:
                    visible.field.widget.attrs["dsrc"] = "dsrc"
                elif type(visible.field.widget) not in self.WIDGETS_NO_FR_INPUT:
                    visible.field.widget.attrs["class"] = "fr-input"

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
        required=False,
    )

    password = forms.CharField(
        label="Mot de passe", required=False, widget=forms.PasswordInput
    )

    sample_number = forms.IntegerField(
        label="Nombre entier",
        help_text="Un nombre inférieur à 0 déclenchera un message d’erreur",
    )

    sample_decimal = forms.DecimalField(
        label="Nombre décimal",
        required=False,
    )

    sample_disabled_field = forms.CharField(
        label="Champ désactivé",
        help_text="Ce champ est désactivé",
        max_length=100,
        disabled=True,
        required=False,
    )

    # date and time
    sample_date = forms.DateField(
        label="Date",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    """
    Not managed by the DSFR:
    - DateTimeField
    """

    # Booleans and choicefields
    sample_boolean = forms.BooleanField(label="Cochez la case", required=False)

    sample_select = forms.ChoiceField(
        label="Liste déroulante",
        required=False,
        choices=[(1, "Option 1"), (2, "Option 2"), (3, "Option 3")],
    )

    sample_multiple_select = forms.MultipleChoiceField(
        label="Liste déroulante à choix multiples",
        required=False,
        choices=[(1, "Option 1"), (2, "Option 2"), (3, "Option 3")],
    )

    sample_radio = forms.ChoiceField(
        label="Boutons radio",
        required=False,
        choices=[(1, "Premier choix"), (2, "Second choix"), (3, "Troisième choix")],
        help_text="Le troisième choix renvoie une erreur s’il est sélectionné",
        widget=forms.RadioSelect,
    )

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

    # text blocks
    sample_comment = forms.CharField(widget=forms.Textarea, required=False)

    sample_json = forms.JSONField(label="Fichier JSON", required=False)

    # files

    sample_file = forms.FileField(label="Pièce jointe", required=False)

    def clean_sample_number(self):
        sample_number = self.cleaned_data["sample_number"]

        if sample_number < 0:
            raise forms.ValidationError("Merci d’entrer un nombre positif")

        return sample_number

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
