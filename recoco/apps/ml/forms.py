from django import forms

from . import models


class ComparisonForm(forms.ModelForm):
    class Meta:
        model = models.Comparison
        fields = ("choice",)
