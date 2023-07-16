from django import forms
from django.contrib import admin

from . import models
from .brevo import Brevo


class EmailTemplateForm(forms.ModelForm):
    def fetch_brevo_templates():
        brevo = Brevo()

        return [(template.id, template.name) for template in brevo.get_templates()]

    sib_id = forms.ChoiceField(
        choices=fetch_brevo_templates, label="Template Brevo", required=True
    )

    class Meta:
        model = models.EmailTemplate
        fields = ["site", "name", "sib_id"]


@admin.register(models.EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateForm

    list_filter = ["site"]
    list_display = ["name", "site"]


# eof
