from django.contrib import admin

from . import models


@admin.register(models.Mesage)
class MessageAdmin(admin.ModelAdmin):
    pass
