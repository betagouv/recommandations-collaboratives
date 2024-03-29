# Generated by Django 3.2.3 on 2021-12-13 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("addressbook", "0004_alter_contact_division"),
        ("home", "0002_alter_userprofile_departments"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="addressbook.organization",
            ),
        ),
    ]
