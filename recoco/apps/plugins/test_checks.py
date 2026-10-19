from django.contrib.sites.models import Site
from django.db import models
from django.test.utils import isolate_apps

from recoco.apps.home.models import SiteConfiguration

from .checks import check_plugin_model, check_plugin_models
from .models import PluginModel


@isolate_apps("recoco.apps.plugins")
def test_plugin_model_subclass_is_valid():
    class Thing(PluginModel):
        class Meta:
            app_label = "plugin_fake"

    assert check_plugin_model(Thing) == []


@isolate_apps("recoco.apps.plugins")
def test_plain_model_is_flagged():
    class Thing(models.Model):
        site = models.ForeignKey(Site, on_delete=models.CASCADE)

        class Meta:
            app_label = "plugin_fake"

    errors = check_plugin_model(Thing)

    assert [e.id for e in errors] == ["plugins.E001"]
    assert errors[0].obj is Thing


@isolate_apps("recoco.apps.plugins")
def test_multi_table_inheritance_from_core_is_exempt():
    class ThingConfig(SiteConfiguration):
        class Meta:
            app_label = "plugin_fake"

    assert check_plugin_model(ThingConfig) == []


@isolate_apps("recoco.apps.plugins")
def test_proxy_and_unmanaged_models_are_exempt():
    class Unmanaged(models.Model):
        class Meta:
            app_label = "plugin_fake"
            managed = False

    class Proxy(Site):
        class Meta:
            app_label = "plugin_fake"
            proxy = True

    assert check_plugin_model(Unmanaged) == []
    assert check_plugin_model(Proxy) == []


@isolate_apps("recoco.apps.plugins")
def test_auto_created_m2m_through_is_exempt():
    class Thing(PluginModel):
        sites = models.ManyToManyField(Site, related_name="+")

        class Meta:
            app_label = "plugin_fake"

    through = Thing._meta.get_field("sites").remote_field.through

    assert check_plugin_model(through) == []


class FakeAppConfig:
    def __init__(self, label, models):
        self.label = label
        self.models = models

    def get_models(self):
        return self.models


@isolate_apps("recoco.apps.plugins")
def test_only_plugin_apps_are_checked():
    class CoreThing(models.Model):
        class Meta:
            app_label = "core_fake"

    class PluginThing(models.Model):
        class Meta:
            app_label = "plugin_fake"

    errors = check_plugin_models(
        app_configs=[
            FakeAppConfig("core_fake", [CoreThing]),
            FakeAppConfig("plugin_fake", [PluginThing]),
        ]
    )

    assert [e.obj for e in errors] == [PluginThing]
