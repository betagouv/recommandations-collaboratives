import uuid

import django
from django.core.files.storage import default_storage
from django.db import migrations, models

import recoco


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

        # todo only delete if save was successful, else report
        with default_storage.open(old_name) as old_file:
            default_storage.save(new_name, old_file)
        default_storage.delete(old_name)

        answer.attachment.name = new_name
        answer.save(update_fields=["attachment"])


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
