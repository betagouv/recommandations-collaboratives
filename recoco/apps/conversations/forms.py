#!/usr/bin/env python


from django import forms
from django.db.models import QuerySet

from recoco.apps.addressbook.models import Contact

from . import models


class MessageForm(forms.ModelForm):
    """Message creation"""

    class Meta:
        model = models.Message
        fields = ["in_reply_to"]

    def set_contact_queryset(self, contact_queryset: QuerySet[Contact]):
        self.fields["contact"].queryset = contact_queryset
