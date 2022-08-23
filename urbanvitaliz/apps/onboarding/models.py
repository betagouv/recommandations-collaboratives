from django.db import models
from dynamic_forms.models import FormField, ResponseField
from urbanvitaliz.apps.projects import models as projects_models


class Onboarding(models.Model):
    form = FormField()


class OnboardingResponse(models.Model):
    onboarding = models.ForeignKey(
        Onboarding, on_delete=models.CASCADE, related_name="responses"
    )
    project = models.OneToOneField(
        projects_models.Project, on_delete=models.CASCADE, related_name="onboarding"
    )

    response = ResponseField()
