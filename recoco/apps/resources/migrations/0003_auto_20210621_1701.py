# Generated by Django 3.2.4 on 2021-06-21 15:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resources", "0002_auto_20210621_1640"),
    ]

    operations = [
        migrations.AddField(
            model_name="resource",
            name="quote",
            field=models.CharField(default="", max_length=256),
        ),
        migrations.AddField(
            model_name="resource",
            name="subtitle",
            field=models.CharField(default="", max_length=128),
        ),
    ]
