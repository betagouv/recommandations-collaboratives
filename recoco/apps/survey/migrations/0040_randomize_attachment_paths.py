import re
import uuid

import django
from django.core.files.storage import default_storage
from django.db import migrations, models, transaction

import recoco


def randomize_attachment_paths(apps, schema_editor):
    """Move existing survey attachments to a path containing a random
    token, so their location can no longer be guessed from the
    sequential session id alone.
    """
    Answer = apps.get_model("survey", "Answer")
    errors = []
    count_missing_files = 0
    count_success_files = 0
    count_already_moved = 0

    for answer in Answer.objects.exclude(attachment="").exclude(
        attachment__isnull=True
    ):
        old_path = answer.attachment.name
        if not old_path or not default_storage.exists(old_path):
            count_missing_files += 1
            continue
        if re.search(r"survey/session/\d+/[^/]+/[^/]+", old_path):
            count_already_moved += 1
            continue

        filename = old_path.rsplit("/", 1)[-1]
        new_path = "survey/session/{0}/{1}/{2}".format(
            answer.session_id, uuid.uuid4().hex, filename
        )

        try:
            with transaction.atomic():
                with default_storage.open(old_path) as old_file:
                    default_storage.save(new_path, old_file)
                answer.attachment.name = new_path
                answer.save(update_fields=["attachment"])
            default_storage.delete(old_path)
            count_success_files += 1
        except Exception as e:
            errors.append(e)
    print(f"\nmissing files: {count_missing_files}")
    print(f"successfully moves files: {count_success_files}")
    print(f"already moved files: {count_already_moved}")
    print(errors)


class Migration(migrations.Migration):
    atomic = False  # resiliency to data loss since migration moves files
    dependencies = [
        ("survey", "0039_sanitize_historic_html_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="answer",
            name="attachment",
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                upload_to=recoco.apps.survey.models.survey_private_file_path,
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
        migrations.RunPython(randomize_attachment_paths, migrations.RunPython.noop),
    ]
