# Generated by Django 4.2.13 on 2024-06-06 14:27

from django.db import migrations


def fill_question_slug_values(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Question = apps.get_model("survey", "Question")
    for question in Question.objects.using(db_alias).filter(slug__isnull=True):
        question.save()

    if Question.objects.using(db_alias).filter(slug__isnull=True).exists():
        raise ValueError(
            "Some questions still have no slug, please fix this migration and re-run it."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0034_question_slug"),
    ]

    operations = [
        migrations.RunPython(
            fill_question_slug_values,
            migrations.RunPython.noop,
        ),
    ]
