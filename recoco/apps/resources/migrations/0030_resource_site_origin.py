# Generated by Django 4.2.13 on 2024-08-02 13:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    def set_site_origin(apps, schema_editor):
        Resource = apps.get_model("resources", "Resource")

        ResourceSite = Resource.sites.through

        for resource in Resource.objects.all():
            resource_site = (
                ResourceSite.objects.filter(resource_id=resource.id)
                .order_by("id")
                .first()
            )
            if resource_site:
                resource.site_origin_id = resource_site.site_id
                resource.save()

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("resources", "0029_remove_resource_old_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="resource",
            name="site_origin",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="authored_resources",
                to="sites.site",
                verbose_name="site d'origine de la ressource",
            ),
        ),
        migrations.RunPython(set_site_origin, migrations.RunPython.noop),
    ]
