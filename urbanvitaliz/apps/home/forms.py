from allauth.account.forms import SignupForm
from django import forms
from urbanvitaliz.apps.addressbook import models as addressbook_models


class UVSignupForm(SignupForm):
    first_name = forms.CharField(max_length=50, required=True, label="Prénom")
    last_name = forms.CharField(max_length=50, required=True, label="Nom")
    organization = forms.CharField(max_length=50, required=True, label="Organisation")

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
