from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0048_merge_20260826_1002"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="siteconfiguration",
            name="sender_email",
        ),
    ]
