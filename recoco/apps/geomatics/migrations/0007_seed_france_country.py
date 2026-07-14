# Generated for geomatics i18n roadmap - phase 1
#
# Seeds the "France" Country and backfills it onto every existing Region.
# See GEOMATIC_I18N.md for the full roadmap this belongs to.

from django.db import migrations

FRANCE_CODE = "FR"
FRANCE_NAME = "France"


def seed_france_and_backfill_regions(apps, schema_editor):
    Country = apps.get_model("geomatics", "Country")
    Region = apps.get_model("geomatics", "Region")

    france, _ = Country.objects.get_or_create(
        code=FRANCE_CODE, defaults={"name": FRANCE_NAME}
    )
    Region.objects.filter(country__isnull=True).update(country=france)


def unseed_france(apps, schema_editor):
    Country = apps.get_model("geomatics", "Country")
    Region = apps.get_model("geomatics", "Region")

    Region.objects.filter(country__code=FRANCE_CODE).update(country=None)
    Country.objects.filter(code=FRANCE_CODE).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("geomatics", "0006_country"),
    ]

    operations = [
        migrations.RunPython(seed_france_and_backfill_regions, unseed_france),
    ]
