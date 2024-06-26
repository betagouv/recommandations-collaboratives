# Generated by Django 4.2.13 on 2024-05-27 12:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0028_siteconfiguration_legal_owner"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteconfiguration",
            name="description",
            field=models.TextField(
                blank=True,
                null=True,
                help_text="Description de 2 à 5 phrases, notamment utilisée dans les emails d'invitation",
                verbose_name="Description",
            ),
        ),
    ]


# eof
