from django.contrib import admin

from . import models


@admin.register(models.ChallengeDefinition)
class ChallengeDefinitionAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(models.Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ["codename", "user", "acquired"]

    def codename(self, obj):
        return obj.challenge_definition.code
