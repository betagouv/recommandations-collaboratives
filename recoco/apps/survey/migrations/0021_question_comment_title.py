# Generated by Django 3.2.3 on 2021-09-06 14:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0020_alter_questionset_deleted"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="comment_title",
            field=models.CharField(
                blank=True,
                default="Commentaire",
                max_length=255,
                verbose_name="Titre du commentaire",
            ),
        ),
    ]
