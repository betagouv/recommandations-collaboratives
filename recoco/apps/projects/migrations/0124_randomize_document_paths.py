import uuid

from django.core.files.storage import default_storage
from django.db import migrations


def randomize_document_paths(apps, schema_editor):
    """Move existing project documents to a path containing a random
    token, so their location can no longer be guessed from the
    sequential project id alone.
    """
    Document = apps.get_model("projects", "Document")

    for document in Document.objects.exclude(the_file="").exclude(
        the_file__isnull=True
    ):
        old_name = document.the_file.name
        if not old_name or not default_storage.exists(old_name):
            continue

        filename = old_name.rsplit("/", 1)[-1]
        new_name = "projects/{0}/{1}/{2}".format(
            document.project_id, uuid.uuid4().hex, filename
        )

        with default_storage.open(old_name) as old_file:
            default_storage.save(new_name, old_file)
        default_storage.delete(old_name)

        document.the_file.name = new_name
        document.save(update_fields=["the_file"])


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0123_sanitize_historic_html_fields"),
    ]

    operations = [
        migrations.RunPython(randomize_document_paths, migrations.RunPython.noop),
    ]
