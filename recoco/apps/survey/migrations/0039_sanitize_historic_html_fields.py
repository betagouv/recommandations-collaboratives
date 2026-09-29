from django.db import migrations

from recoco.utils import sanitize_text_field_historic_data


def sanitize_html_fields(apps, schema_editor):
    """Retroactively apply the sanitization of filds to be
    safe in information_card.html) to values already stored in the database.
    """
    db_alias = schema_editor.connection.alias

    Answer = apps.get_model("survey", "Answer")
    sanitize_text_field_historic_data(Answer, "comment", db_alias)

    Choice = apps.get_model("survey", "Choice")
    sanitize_text_field_historic_data(Choice, "conclusion", db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0038_questionset_precondition_tags"),
    ]

    operations = [
        migrations.RunPython(
            sanitize_html_fields,
            migrations.RunPython.noop,
        ),
    ]
