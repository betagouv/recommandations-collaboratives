from django.contrib import admin
from django.contrib.auth import models as auth_models
from django.contrib.auth.admin import UserAdmin

from . import models


class ProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "organization",
    )
    list_select_related = ("profile",)

    def organization(self, instance):
        return instance.profile.organization

    organization.short_description = "Organization"

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()

        return super().get_inline_instances(request, obj)


admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, CustomUserAdmin)
