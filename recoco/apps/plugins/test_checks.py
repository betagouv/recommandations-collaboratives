import pluggy
import pytest
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.test.utils import isolate_apps

from recoco.apps.home.models import SiteConfiguration

from .checks import (
    check_plugin_model,
    check_plugin_models,
    check_plugin_name,
    check_plugin_names,
)
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
    def __init__(self, label, models=None, name=None):
        self.label = label
        self.models = models or []
        self.name = name or label

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


def test_plugin_named_like_its_app_label_is_valid():
    app_configs = [FakeAppConfig("plugin_fake")]

    assert check_plugin_name("plugin_fake", app_configs) == []


def test_plugin_without_prefix_is_flagged():
    app_configs = [FakeAppConfig("fake")]

    errors = check_plugin_name("fake", app_configs)

    assert [e.id for e in errors] == ["plugins.E002"]


def test_plugin_with_another_app_label_is_flagged():
    app_configs = [FakeAppConfig("custom_label", name="plugin_fake")]

    errors = check_plugin_name("plugin_fake", app_configs)

    assert [e.id for e in errors] == ["plugins.E003"]


def test_installed_plugins_pass_the_checks():
    assert check_plugin_names() == []


# --- SiteConfiguration.enabled_plugins ---


@pytest.fixture
def installed_plugins(monkeypatch):
    def install(*names):
        pm = pluggy.PluginManager("recoco")
        for name in names:
            pm.register(object(), name=name)
        monkeypatch.setattr("recoco.apps.plugins.manager._plugin_manager", pm)

    return install


def test_enabled_plugins_must_be_installed(installed_plugins):
    installed_plugins("plugin_fake")

    SiteConfiguration(enabled_plugins=["plugin_fake"]).clean()

    with pytest.raises(ValidationError) as excinfo:
        SiteConfiguration(enabled_plugins=["plugin_fake", "plugin_typo"]).clean()
    assert "plugin_typo" in str(excinfo.value.message_dict["enabled_plugins"])
