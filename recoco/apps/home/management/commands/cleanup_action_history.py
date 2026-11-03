"""
Pour un utilisateur donné, on conserve :

    maximum 30 traces d'activité
    maximum 15 traces de connexion
    jusqu'à maximum 2 ans

"""

from datetime import timedelta

from actstream.models import Action
from django.core.management import BaseCommand
from django.utils import timezone

from recoco.apps.home.utils import DELETION_ABSENT_FOR_DAYS


class Command(BaseCommand):
    help = "Delete actions ('traces') that are too old"

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            help="Do not actually delete any action",
        )

    def cleanup_old_actions(self, dry_run):
        now = timezone.now()
        so_long = now - timedelta(days=DELETION_ABSENT_FOR_DAYS)
        to_delete = Action.objects.filter(timestamp__lt=so_long)

        self.stdout.write(f"{to_delete.count()} actions to be deleted")
        if dry_run:
            self.stdout.write("dry run: no actions deleted")
        else:
            to_delete.delete()
            self.stdout.write("deletion successful")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        self.cleanup_old_actions(dry_run)
