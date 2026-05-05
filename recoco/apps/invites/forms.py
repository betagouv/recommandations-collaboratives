# encoding: utf-8

"""
Forms for invites application

author  : guillaume.libersat@beta.gouv.fr,raphael.marvie@beta.gouv.fr
created : 2022-04-19 14:16:20 CEST
"""

from django import forms
from django.contrib.auth import models as auth_models
from django.contrib.auth.forms import SetPasswordMixin
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from recoco.apps.addressbook import models as addressbook_models

from . import models


class InviteForm(forms.ModelForm):
    """Standard form for invitations"""

    class Meta:
        model = models.Invite
        fields = ["email", "message"]


class InviteAcceptForm(SetPasswordMixin, forms.Form):
    """Complementary informations when accepting an invitation"""

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    organization = forms.CharField(required=True)
    position = forms.CharField(required=True)
    phone_no = PhoneNumberField(
        required=True,
        label="Numéro de téléphone",
        widget=PhoneNumberInternationalFallbackWidget(),
    )
    password, password_confirm = SetPasswordMixin.create_password_fields()

    def clean(self):
        self.validate_passwords("password", "password_confirm")
        return super().clean()

    def __init__(self, *args, **kwargs):
        self.invite = kwargs.pop("invite")
        self.site = kwargs.pop("site")
        super().__init__(*args, **kwargs)

    def _post_clean(self):
        super()._post_clean()
        self.user = auth_models.User(
            username=self.invite.email,
            email=self.invite.email,
            first_name=self.cleaned_data.get("first_name"),
            last_name=self.cleaned_data.get("last_name"),
        )
        self.validate_password_for_user(self.user, "password")

    def save(self):
        self.set_password_and_save(self.user, "password")

        org_name = self.cleaned_data.get("organization")
        organization = addressbook_models.Organization.get_or_create(org_name)
        organization.sites.add(self.site)

        self.user.profile.organization = organization
        self.user.profile.organization_position = self.cleaned_data.get("position")
        self.user.profile.phone_no = self.cleaned_data.get("phone_no")

        self.user.profile.save()
        return self.user
