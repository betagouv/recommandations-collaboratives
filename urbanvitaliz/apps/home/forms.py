from allauth.account.forms import SignupForm, LoginForm, ResetPasswordForm, ResetPasswordKeyForm
from django import forms
from urbanvitaliz.apps.addressbook import models as addressbook_models


class UVSignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        super(UVSignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'fr-input fr-mt-2v fr-mb-4v'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'fr-input fr-mt-2v fr-mb-4v'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'fr-input fr-mt-2v fr-mb-4v'})

    first_name = forms.CharField(max_length=50, required=True, label="Prénom", widget=forms.TextInput(attrs={'class': 'fr-input fr-mt-2v fr-mb-4v'}))
    last_name = forms.CharField(max_length=50, required=True, label="Nom", widget=forms.TextInput(attrs={'class': 'fr-input fr-mt-2v fr-mb-4v'}))
    organization = forms.CharField(max_length=50, required=True, label="Organisation", widget=forms.TextInput(attrs={'class': 'fr-input fr-mt-2v fr-mb-4v'}))

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super().save(request)

        data = self.cleaned_data

        organization, _ = addressbook_models.Organization.objects.get_or_create(
            name__iexact=data.get("organization")
        )
        user.profile.organization = organization
        user.profile.save()

        return user

class UVLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(UVLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'fr-input fr-mt-2v fr-mb-4v'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'fr-input fr-mt-2v fr-mb-4v'})

class UVResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(UVResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'fr-input fr-mt-2v fr-mb-4v'})

class UVResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(UVResetPasswordKeyForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'fr-input fr-mt-2v fr-mb-4v'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'fr-input fr-mt-2v fr-mb-4v'})
