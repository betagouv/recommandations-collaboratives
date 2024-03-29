# Generated by Django 3.2.13 on 2022-05-17 08:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0048_task_order"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taskfollowup",
            name="status",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (0, "proposé"),
                    (1, "en cours"),
                    (2, "blocage"),
                    (3, "terminé"),
                    (4, "pas intéressé·e"),
                    (5, "déjà fait"),
                ],
                null=True,
            ),
        ),
    ]
