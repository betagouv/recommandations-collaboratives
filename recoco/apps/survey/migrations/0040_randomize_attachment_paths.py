import uuid

from django.core.files.storage import default_storage
from django.db import migrations


def randomize_attachment_paths(apps, schema_editor):
    """Move existing survey attachments to a path containing a random
    token, so their location can no longer be guessed from the
    sequential session id alone.
    """
    Answer = apps.get_model("survey", "Answer")

    for answer in Answer.objects.exclude(attachment="").exclude(
        attachment__isnull=True
    ):
        old_name = answer.attachment.name
        if not old_name or not default_storage.exists(old_name):
            continue

        filename = old_name.rsplit("/", 1)[-1]
        new_name = "survey/session/{0}/{1}/{2}".format(
            answer.session_id, uuid.uuid4().hex, filename
        )

        with default_storage.open(old_name) as old_file:
            default_storage.save(new_name, old_file)
        default_storage.delete(old_name)

        answer.attachment.name = new_name
        answer.save(update_fields=["attachment"])


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0039_sanitize_historic_html_fields"),
    ]

    operations = [
        migrations.RunPython(randomize_attachment_paths, migrations.RunPython.noop),
    ]
