from django.core.management.base import BaseCommand
from recoco.apps.metrics.metabase import clone_collection


class Command(BaseCommand):
    help = "Create Metabase Dashboard for a new site"

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--source-collection-id",
            type=int,
            help="Id of the collection to duplicate",
        )
        parser.add_argument(
            "-t", "--target-schema", type=str, help="Target database schema name"
        )
        parser.add_argument(
            "-n",
            "--new-collection-name",
            type=str,
            help="Name of new collection to create",
        )

    def handle(self, *args, **options):
        clone_collection(
            options["source_collection_id"],
            options["new_collection_name"],
            options["target_schema"],
        )
