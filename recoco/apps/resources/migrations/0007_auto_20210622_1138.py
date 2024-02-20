# Generated by Django 3.2.4 on 2021-06-22 09:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resources", "0006_alter_resource_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resource",
            name="quote",
            field=models.CharField(default="", max_length=512),
        ),
        migrations.AlterField(
            model_name="resource",
            name="subtitle",
            field=models.CharField(default="", max_length=512),
        ),
        migrations.AlterField(
            model_name="resource",
            name="title",
            field=models.CharField(max_length=256),
        ),
    ]