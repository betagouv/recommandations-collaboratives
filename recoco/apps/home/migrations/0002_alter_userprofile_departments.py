# Generated by Django 3.2.3 on 2021-11-16 16:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("geomatics", "0003_alter_department_code"),
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="departments",
            field=models.ManyToManyField(
                blank=True, related_name="user_profiles", to="geomatics.Department"
            ),
        ),
    ]
