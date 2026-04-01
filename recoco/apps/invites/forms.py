# encoding: utf-8

"""
Forms for invites application

author  : guillaume.libersat@beta.gouv.fr,raphael.marvie@beta.gouv.fr
created : 2022-04-19 14:16:20 CEST
"""

from django import forms

from . import models


class InviteForm(forms.ModelForm):
    """Standard form for invitations"""

    class Meta:
        model = models.Invite
        fields = ["email", "message"]


class InviteAcceptForm(forms.Form):
    """Complementary informations when accepting an invitation"""

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    organization = forms.CharField(required=True)
    position = forms.CharField(required=True)
    phone_no = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error(
                "password_confirm", "Les mots de passe ne correspondent pas."
            )
        return cleaned_data
