# Generated by Django 3.2.3 on 2021-11-01 13:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0028_auto_20211011_1308"),
    ]

    operations = [
        migrations.AddField(
            model_name="answer",
            name="choices",
            field=models.ManyToManyField(related_name="answers", to="survey.Choice"),
        ),
    ]
