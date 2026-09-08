from django.db import migrations

from recoco.utils import sanitize_text_field_historic_data


def sanitize_html_fields(apps, schema_editor):
    """Retroactively apply the sanitization of filds to be
    safe in information_card.html) to values already stored in the database.
    """
    Project = apps.get_model("projects", "Project")
    db_alias = schema_editor.connection.alias

    for field_name in ("description", "advisors_note"):
        sanitize_text_field_historic_data(Project, field_name, db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0122_alter_project_options_alter_project_managers"),
    ]

    operations = [
        migrations.RunPython(
            sanitize_html_fields,
            migrations.RunPython.noop,
        ),
    ]
