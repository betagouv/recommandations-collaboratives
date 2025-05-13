from django.db import migrations, transaction
from django.db.models import Value
from django.db.models.functions import Replace


def update_verbs(apps, schema_editor):
    Notification = apps.get_model("notifications", "Notification")
    Action = apps.get_model("actstream", "Action")

    # Bulk update the verb field
    old_term = "projet"
    new_term = "dossier"

    with transaction.atomic():
        Notification.objects.filter(verb__icontains=old_term).update(
            verb=Replace("verb", Value(old_term), Value(new_term))
        )

        Action.objects.filter(verb__icontains=old_term).update(
            verb=Replace("verb", Value(old_term), Value(new_term))
        )


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0035_alter_siteconfiguration_accept_handover_and_more"),
    ]

    operations = [
        migrations.RunPython(
            code=update_verbs,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
