import uuid

import django.core.validators
import recoco.apps.projects.models
import recoco.apps.projects.validators
from django.db import migrations, models
from django.core.files.storage import default_storage


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

        # todo only delete if save was successful, else report
        with default_storage.open(old_name) as old_file:
            default_storage.save(new_name, old_file)
        default_storage.delete(old_name)

        document.the_file.name = new_name
        document.save(update_fields=["the_file"])


class Migration(migrations.Migration):
    atomic = False  # resiliency to data loss since migration moves files
    dependencies = [
        ("projects", "0123_sanitize_historic_html_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="the_file",
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                upload_to=recoco.apps.projects.models.Document.upload_path,
                validators=[
                    recoco.apps.projects.validators.MimetypeValidator(
                        allows=[
                            "text/plain",
                            "image/png",
                            "image/jpg",
                            "image/gif",
                            "image/jpeg",
                            "image/pjpeg",
                            "application/pdf",
                            "application/msword",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "application/vnd.oasis.opendocument.text",
                            "application/vnd.ms-excel",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            "application/vnd.oasis.opendocument.spreadsheet",
                            "application/vnd.ms-powerpoint",
                            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            "application/vnd.oasis.opendocument.presentation",
                            "application/x-zip-compressed",
                            "application/zip",
                        ]
                    ),
                    django.core.validators.FileExtensionValidator(
                        [
                            "txt",
                            "md",
                            "png",
                            "jpg",
                            "jpeg",
                            "pdf",
                            "doc",
                            "docx",
                            "odt",
                            "xls",
                            "xlsx",
                            "odc",
                            "ppt",
                            "pptx",
                            "odp",
                            "zip",
                        ]
                    ),
                ],
            ),
        ),
        migrations.RunPython(randomize_document_paths, migrations.RunPython.noop),
    ]
