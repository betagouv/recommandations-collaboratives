from django.contrib import admin

from . import models


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "organization"]
    ordering = ["user__username", "organization"]
