# Generated by Django 4.2.11 on 2024-03-14 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("communication", "0011_alter_transactionrecord_transaction_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailtemplate",
            name="site",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="sites.site",
            ),
        ),
    ]
