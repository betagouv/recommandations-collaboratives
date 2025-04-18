# Generated by Django 4.2.13 on 2024-05-22 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("django_webhook", "0004_alter_webhookevent_created_and_more"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebhookSite",
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
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webhooksites",
                        to="sites.site",
                    ),
                ),
                (
                    "webhook",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webhooksite",
                        to="django_webhook.webhook",
                    ),
                ),
            ],
            options={
                "verbose_name": "Webhook Site",
                "verbose_name_plural": "Webhook Sites",
                "unique_together": {("webhook", "site")},
            },
        ),
    ]
