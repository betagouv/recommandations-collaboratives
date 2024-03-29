# Generated by Django 3.2.4 on 2021-06-21 14:40

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("resources", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=128)),
                ("color", models.CharField(max_length=16)),
                ("icon", models.CharField(max_length=32)),
                ("deleted", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "catégorie",
                "verbose_name_plural": "catégories",
            },
        ),
        migrations.AlterField(
            model_name="resource",
            name="created_on",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="dernière modification"
            ),
        ),
        migrations.AddField(
            model_name="resource",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="resources.category",
            ),
        ),
    ]
