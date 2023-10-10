# Generated by Django 3.2.18 on 2023-10-10 06:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0093_project_last_members_activity_at"),
        ("sites", "0002_alter_domain_unique"),
        ("reminders", "0006_auto_20220614_1453"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectReminderState",
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
                    "last_sent_on",
                    models.DateField(
                        blank=True,
                        editable=False,
                        null=True,
                        verbose_name="Quand les derniers rappels ont été envoyés",
                    ),
                ),
                (
                    "state",
                    models.PositiveIntegerField(
                        default=0,
                        editable=False,
                        verbose_name="Etat d'avancement de la fréquence des rappels",
                    ),
                ),
                (
                    "project",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reminder_state",
                        to="projects.project",
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="project_reminders_state",
                        to="sites.site",
                    ),
                ),
            ],
        ),
    ]