# Generated by Django 4.2.11 on 2024-08-02 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0102_alter_projectswitchtender_managers_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="location",
            field=models.CharField(
                blank=True, max_length=256, null=True, verbose_name="Localisation"
            ),
        ),
    ]