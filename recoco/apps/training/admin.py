from django.contrib import admin

from . import models


@admin.register(models.ChallengeDefinition)
class ChallengeDefinitionAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "site"]

    list_filter = ["site"]


@admin.register(models.Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ["codename", "user", "acquired_on"]

    def codename(self, obj):
        return obj.challenge_definition.code
