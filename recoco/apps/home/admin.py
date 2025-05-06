from csvexport.actions import csvexport
from django.contrib import admin
from django.contrib.auth import models as auth_models
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from . import models


@admin.register(models.SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ("site", "project_survey")


class ProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class IsMultipleSiteFilter(admin.SimpleListFilter):
    title = "Muti-site"
    parameter_name = "multisite"

    def lookups(self, request, model_admin):
        return (("yes", "Yes"), ("no", "No"))

    def queryset(self, request, queryset):
        queryset = queryset.annotate(sites_count=Count("profile__sites"))
        if self.value() == "yes":
            return queryset.filter(sites_count__gt=1)
        if self.value() == "no":
            return queryset.filter(sites_count=1)


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "organization",
        "sites",
    )

    actions = [csvexport]

    list_filter = (
        "date_joined",
        "is_staff",
        "is_superuser",
        "is_active",
        IsMultipleSiteFilter,
        "groups",
        "profile__sites",
    )

    list_per_page = 50

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("profile__sites")
            .select_related("profile__organization")
        )

    @admin.display(description="Organization")
    def organization(self, instance):
        return instance.profile.organization

    @admin.display(description="Sites")
    def sites(self, instance):
        return ",".join([site.name for site in instance.profile.sites.all()])

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()

        return super().get_inline_instances(request, obj)


admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, CustomUserAdmin)


@admin.register(models.AdvisorAccessRequest)
class AdvisorAccessRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "status",
    )
    list_filter = (
        "site",
        "status",
    )
    ordering = ("-created",)
    readonly_fields = ("handled_by",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "handled_by")
            .prefetch_related("departments")
        )
