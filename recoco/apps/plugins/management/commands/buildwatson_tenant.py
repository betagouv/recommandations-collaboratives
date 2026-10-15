from watson.management.commands.buildwatson import Command as BuildWatsonCommand

from recoco.apps.plugins.schema import all_schema_context


class Command(BuildWatsonCommand):
    help = (
        "Rebuilds the database indices needed by django-watson. "
        "You can (re-)build index for selected models by specifying them,"
        " including all tenant schemas"
    )

    def handle(self, *args, **options):
        with all_schema_context():
            super().handle(*args, **options)
