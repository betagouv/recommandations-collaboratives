from django.db import models
from dynamic_forms.models import FormField, ResponseField


class Onboarding(models.Model):
    form = FormField(
        default=[
            {
                "type": "text",
                "required": False,
                "label": "Vide",
                "className": "form-control",
                "name": "text-0000000000000-0",
                "subtype": "text",
            }
        ]
    )


class OnboardingResponse(models.Model):
    onboarding = models.ForeignKey(
        Onboarding, on_delete=models.CASCADE, related_name="responses"
    )
    project = models.OneToOneField(
        "projects.Project", on_delete=models.CASCADE, related_name="onboarding"
    )

    response = ResponseField()
