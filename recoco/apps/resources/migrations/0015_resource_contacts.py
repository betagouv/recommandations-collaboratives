# Generated by Django 3.2.3 on 2021-07-26 15:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("addressbook", "0002_auto_20210720_0948"),
        ("resources", "0014_alter_resource_departments"),
    ]

    operations = [
        migrations.AddField(
            model_name="resource",
            name="contacts",
            field=models.ManyToManyField(
                blank=True, to="addressbook.Contact", verbose_name="Contacts associés"
            ),
        ),
    ]
