from django.contrib import admin

from . import models


@admin.register(models.LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LLMPrompt)
class LLMPromptAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Summary)
class SummaryAdmin(admin.ModelAdmin):
    pass
