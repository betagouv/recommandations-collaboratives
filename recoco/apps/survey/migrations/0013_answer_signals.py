# Generated by Django 3.2.3 on 2021-08-09 13:20

from django.db import migrations
import tagging.fields


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0012_question_precondition"),
    ]

    operations = [
        migrations.AddField(
            model_name="answer",
            name="signals",
            field=tagging.fields.TagField(
                blank=True, max_length=255, null=True, verbose_name="Signaux"
            ),
        ),
    ]
