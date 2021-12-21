from django import forms
from django.contrib import admin

from . import models
from .sendinblue import SendInBlue


class EmailTemplateForm(forms.ModelForm):
    def fetch_sib_templates():
        sib = SendInBlue()

        return [(template.id, template.name) for template in sib.get_templates()]

    sib_id = forms.ChoiceField(
        choices=fetch_sib_templates, label="Template SendInBlue", required=True
    )

    class Meta:
        model = models.EmailTemplate
        fields = ["name", "sib_id"]


@admin.register(models.EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateForm


# eof
