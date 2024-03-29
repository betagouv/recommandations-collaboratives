# Generated by Django 3.2.9 on 2021-11-15 13:49

from django.db import migrations

from django.contrib.auth import models as auth


def create_switchtender_group(apps, schema_editor):
    """Create the switchtender group for their permissions"""
    g, _ = auth.Group.objects.get_or_create(name="switchtender")


def delete_switchtender_group(apps, schema_editor):
    """Delete the switchtender group"""
    auth.Group.objects.filter(name="switchtender").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0034_alter_project_options"),
    ]

    operations = [
        migrations.RunPython(create_switchtender_group, delete_switchtender_group),
    ]
