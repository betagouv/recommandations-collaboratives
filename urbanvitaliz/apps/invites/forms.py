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
        fields = ["email", "role", "message"]


class InviteAcceptForm(forms.Form):
    """Complementary informations when accepting an invitation"""

    first_name = forms.CharField()
    last_name = forms.CharField()
    organization = forms.CharField()
    position = forms.CharField()
