# Generated by Django 3.2.3 on 2022-01-04 16:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0040_remove_project_is_draft"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="notes_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
