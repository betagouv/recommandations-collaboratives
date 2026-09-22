import re
import uuid

import django.core.validators
from tqdm import tqdm

import recoco.apps.projects.models
import recoco.apps.home.validators
from django.db import migrations, models, transaction
from django.core.files.storage import default_storage


def randomize_document_paths(apps, schema_editor):
    """Move existing project documents to a path containing a random
    token, so their location can no longer be guessed from the
    sequential project id alone.
    """
    Document = apps.get_model("projects", "Document")
    errors = []
    count_missing_files = 0
    count_success_files = 0
    count_already_moved = 0

    for document in tqdm(
        Document.objects.exclude(the_file="").exclude(the_file__isnull=True)
    ):
        old_path = document.the_file.name
        if not old_path or not default_storage.exists(old_path):
            count_missing_files += 1
            continue

        filename = old_path.rsplit("/", 1)[-1]
        new_path = "projects/{0}/{1}/{2}".format(
            document.project_id, uuid.uuid4().hex, filename
        )
        if re.search(r"projects/\d+/[^/]+/[^/]+", old_path):
            count_already_moved += 1
            continue

        try:
            with transaction.atomic():
                with default_storage.open(old_path) as old_file:
                    default_storage.save(new_path, old_file)
                document.the_file.name = new_path
                document.save(update_fields=["the_file"])
            default_storage.delete(old_path)
            count_success_files += 1
        except Exception as e:
            errors.append(e)
    print(f"\nmissing files: {count_missing_files}")
    print(f"already moved files: {count_already_moved}")
    print(f"successfully moves files: {count_success_files}")
    print(errors)


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
                    recoco.apps.home.validators.MimetypeValidator(
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
