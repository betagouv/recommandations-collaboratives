from allauth.account.forms import (
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SignupForm,
)
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from urbanvitaliz.apps.addressbook import models as addressbook_models


class UVSignupForm(SignupForm):
    field_order = [
        "first_name",
        "last_name",
        "organization",
        "organization_position",
        "email",
        "phone_no",
        "password1",
        "password2",
        "captcha",
    ]

    def __init__(self, *args, **kwargs):
        super(UVSignupForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget = forms.TextInput(
            attrs={"type": "email", "class": "fr-input fr-mt-2v fr-mb-4v"}
        )
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )

    first_name = forms.CharField(
        max_length=50,
        required=True,
        label="Prénom",
        widget=forms.TextInput(attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}),
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label="Nom",
        widget=forms.TextInput(attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}),
    )
    organization = forms.CharField(
        max_length=50,
        required=True,
        label="Organisation",
        widget=forms.TextInput(attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}),
    )

    organization_position = forms.CharField(
        max_length=50,
        required=True,
        label="Fonction",
        widget=forms.TextInput(attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}),
    )

    phone_no = PhoneNumberField(
        required=False,
        label="Numéro de téléphone",
        widget=PhoneNumberInternationalFallbackWidget(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        ),
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(api_params={"hl": "fr"}))

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super().save(request)

        data = self.cleaned_data

        org_name = data.get("organization")
        organization, _ = addressbook_models.Organization.objects.get_or_create(
            name__iexact=org_name, defaults={"name": org_name}
        )
        user.profile.organization = organization
        user.profile.organization_position = data["organization_position"]
        user.profile.phone_no = data.get("phone_no", None)
        user.profile.save()

        return user


class UVLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(UVLoginForm, self).__init__(*args, **kwargs)
        self.fields["login"].widget = forms.TextInput(
            attrs={"type": "email", "class": "fr-input fr-mt-2v fr-mb-4v"}
        )
        self.fields["password"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )


class UVResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(UVResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget = forms.TextInput(
            attrs={"type": "email", "class": "fr-input fr-mt-2v fr-mb-4v"}
        )


class UVResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(UVResetPasswordKeyForm, self).__init__(*args, **kwargs)
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"class": "fr-input fr-mt-2v fr-mb-4v"}
        )
