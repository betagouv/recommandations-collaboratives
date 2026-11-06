#!/usr/bin/env python


from django import forms

from recoco.apps.addressbook.models import Contact

from . import models


class MessageForm(forms.ModelForm):
    """Message creation"""

    class Meta:
        model = models.Message
        fields = ["in_reply_to"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact"].queryset = Contact.on_site
