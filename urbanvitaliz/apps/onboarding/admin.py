from django.contrib import admin

from . import models


@admin.register(models.Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    pass


@admin.register(models.OnboardingResponse)
class OnboardingResponseAdmin(admin.ModelAdmin):
    pass
