# Generated by Django 5.1.9 on 2025-06-10 07:56

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("resources", "0031_resource_imported_from"),
        ("tasks", "0006_taskfollowup_contact_alter_task_contact"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResourceAddon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=False,
                        help_text="Indique si l'addon est activé pour cette ressource",
                    ),
                ),
                (
                    "nature",
                    models.CharField(help_text="Nature de l'addon", max_length=32),
                ),
                (
                    "data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Contenu additionnel de la ressource, au format JSON",
                    ),
                ),
                (
                    "recommendation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resource_addons",
                        to="tasks.task",
                    ),
                ),
            ],
            options={
                "verbose_name": "Addon de ressource",
                "verbose_name_plural": "Addons de ressources",
                "ordering": ["-created"],
                "unique_together": {("recommendation", "nature")},
            },
        ),
    ]
