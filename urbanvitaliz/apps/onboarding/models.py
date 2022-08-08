from django.db import models
from dynamic_forms.models import FormField, ResponseField


class Onboarding(models.Model):
    form = FormField()


class OnboardingResponse(models.Model):
    onboarding = models.ForeignKey(
        Onboarding, on_delete=models.CASCADE, related_name="responses"
    )
    response = ResponseField()
