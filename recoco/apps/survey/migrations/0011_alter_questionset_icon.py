# Generated by Django 3.2.3 on 2021-08-09 12:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0010_alter_choice_signals"),
    ]

    operations = [
        migrations.AlterField(
            model_name="questionset",
            name="icon",
            field=models.CharField(blank=True, max_length=80, verbose_name="Icône"),
        ),
    ]
