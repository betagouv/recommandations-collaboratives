from csvexport.actions import csvexport
from django.contrib import admin

from . import models


@admin.register(models.Note)
class NoteAdmin(admin.ModelAdmin):
    actions = [csvexport]
    list_filter = ["site", "kind"]
