# Generated by Django 4.2.16 on 2025-01-28 09:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0033_siteconfiguration_main_topic"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteconfiguration",
            name="crisp_token",
            field=models.CharField(
                blank=True, null=True, verbose_name="Clé pour activer CRISP"
            ),
        ),
    ]
