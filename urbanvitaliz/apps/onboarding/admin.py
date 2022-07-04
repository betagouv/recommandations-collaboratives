from django.contrib import admin

from . import models


@admin.register(models.Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    pass
