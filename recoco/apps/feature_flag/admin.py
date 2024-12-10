from django.contrib import admin
from django.contrib.sites.models import Site
from waffle.admin import FlagAdmin as BaseFlagAdmin
from waffle.admin import SampleAdmin as BaseSampleAdmin
from waffle.admin import SwitchAdmin as BaseSwitchAdmin

from .models import Flag, Sample, Switch


class FFAdminSiteFilter(admin.SimpleListFilter):
    title = "site"
    parameter_name = "site"

    def lookups(self, request, model_admin):
        return [(site.id, site.name) for site in Site.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sites=self.value())
        return queryset


class FFAdminMixin:
    @admin.display(description="Sites")
    def list_sites(self, obj):
        return ", ".join([site.name for site in obj.sites.all()])


@admin.register(Switch)
class SwitchAdmin(FFAdminMixin, BaseSwitchAdmin):
    list_display = BaseSwitchAdmin.list_display + ("list_sites",)
    list_filter = BaseSwitchAdmin.list_filter + (FFAdminSiteFilter,)


@admin.register(Flag)
class FlagAdmin(FFAdminMixin, BaseFlagAdmin):
    list_display = BaseFlagAdmin.list_display + ("list_sites",)
    list_filter = BaseFlagAdmin.list_filter + (FFAdminSiteFilter,)


@admin.register(Sample)
class SampleAdmin(FFAdminMixin, BaseSampleAdmin):
    list_display = BaseSampleAdmin.list_display + ("list_sites",)
    list_filter = BaseSampleAdmin.list_filter + (FFAdminSiteFilter,)
