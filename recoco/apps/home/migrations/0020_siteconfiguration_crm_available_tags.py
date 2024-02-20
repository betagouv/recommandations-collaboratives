# Generated by Django 3.2.23 on 2023-12-20 13:48

from django.db import migrations
import taggit.managers


def set_default_tags(apps, schema_editor):
    tag_slugs_to_add = ["crm_diag", "crm_edl", "crm_contact", "crm_general"]

    Tag = apps.get_model("taggit", "Tag")
    TaggedItem = apps.get_model("taggit", "TaggedItem")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type, _created = ContentType.objects.get_or_create(
        app_label="home", model="siteconfiguration"
    )

    SiteConfiguration = apps.get_model("home", "SiteConfiguration")
    for site_conf in SiteConfiguration.objects.all():
        for slug in tag_slugs_to_add:
            try:
                tag = Tag.objects.get(slug__iexact=slug)
            except Tag.DoesNotExist:
                continue

            tagged_items, _ = TaggedItem.objects.get_or_create(
                content_type_id=content_type.id, object_id=site_conf.id, tag=tag
            )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0019_alter_siteconfiguration_reminder_interval"),
        ("crm", "0010_new_crm_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteconfiguration",
            name="crm_available_tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text=(
                    "Liste de tags séparés par une virgule. "
                    "Attention, veillez à ne pas retirer un tag utilisé dans un projet,"
                    " celui-ci ne pourra plus être retiré depuis le CRM"
                ),
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Étiquettes projets disponibles dans le CRM",
            ),
        ),
        migrations.RunPython(set_default_tags, migrations.RunPython.noop),
    ]