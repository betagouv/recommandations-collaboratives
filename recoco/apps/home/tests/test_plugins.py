import pytest
from django.contrib.sites.models import Site
from model_bakery import baker

from recoco.apps.home.models import SiteConfiguration


@pytest.mark.django_db
def test_schema_name_auto_generated_when_plugins_enabled():
    site = baker.make(Site, domain="my-portal.example.com")
    sc = baker.make(SiteConfiguration, site=site, schema_name=None, enabled_plugins=[])

    sc.enabled_plugins = ["plugin_mi_depafi"]
    sc.save()

    sc.refresh_from_db()
    assert sc.schema_name == "my_portal_example_com"


@pytest.mark.django_db
def test_schema_name_not_overwritten_when_already_set():
    site = baker.make(Site, domain="my-portal.example.com")
    sc = baker.make(
        SiteConfiguration,
        site=site,
        schema_name="custom_schema",
        enabled_plugins=[],
    )

    sc.enabled_plugins = ["plugin_mi_depafi"]
    sc.save()

    sc.refresh_from_db()
    assert sc.schema_name == "custom_schema"


@pytest.mark.django_db
def test_schema_name_not_generated_when_no_plugins():
    site = baker.make(Site, domain="my-portal.example.com")
    sc = baker.make(SiteConfiguration, site=site, schema_name=None, enabled_plugins=[])

    sc.save()

    sc.refresh_from_db()
    assert sc.schema_name is None
