# Generated by Django 3.2.8 on 2021-10-11 14:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0025_rename_accepted_task_visited"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="description",
            field=models.TextField(blank=True, default="", verbose_name="Description"),
        ),
    ]
