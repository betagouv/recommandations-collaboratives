# Generated by Django 4.2.12 on 2024-05-28 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("projects", "0095_alter_document_uploaded_by"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="site",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="project_notes",
                to="sites.site",
            ),
        ),
    ]