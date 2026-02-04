from datetime import datetime, timedelta

from django.core.management import BaseCommand
from tqdm import tqdm

from recoco.apps.home.models import UserProfile
from recoco.apps.home.utils import (
    DELETION_ABSENT_FOR_DAYS,
    FIRST_WARNING_DAYS_BEFORE,
    SECOND_WARNING_DAYS_BEFORE,
    delete_user,
    send_deletion_warning_to_profiles,
)


class Command(BaseCommand):
    help = "Warn and delete users that have been absent for too long"

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--dry-run", action="store_true", help="Do not actually send stuff"
        )

    def warn_and_delete(self, dry_run):
        now = datetime.now()
        so_long = now - timedelta(days=DELETION_ABSENT_FOR_DAYS)
        since_second_warning = now - timedelta(days=SECOND_WARNING_DAYS_BEFORE)
        since_first_warning = now - timedelta(
            days=FIRST_WARNING_DAYS_BEFORE - SECOND_WARNING_DAYS_BEFORE
        )

        not_deleted_profiles = UserProfile.objects.exclude(
            user__last_name="Compte supprimé"
        )

        # resets warning of users who used the platform lately
        not_deleted_profiles.filter(
            previous_activity_at__gte=since_second_warning, nb_deletion_warnings__gt=0
        ).update(nb_deletion_warnings=0, previous_deletion_warning_at=None)

        # first warning
        to_first_warn_profiles = not_deleted_profiles.filter(
            previous_activity_at__lt=so_long, nb_deletion_warnings=0
        )
        self.stdout.write(
            f"Warning {to_first_warn_profiles.count()} users for the first time"
        )
        if dry_run:
            self.stdout.write("dry run: no email sent")
        else:
            send_deletion_warning_to_profiles(to_first_warn_profiles, 1)
            to_first_warn_profiles.update(
                nb_deletion_warnings=1, previous_deletion_warning_at=datetime.now()
            )

        # second warning
        to_second_warn_profiles = not_deleted_profiles.filter(
            previous_deletion_warning_at__lt=since_first_warning, nb_deletion_warnings=1
        )
        self.stdout.write(
            f"Warning {to_second_warn_profiles.count()} users for the second time"
        )
        if dry_run:
            self.stdout.write("dry run: no email sent")
        else:
            send_deletion_warning_to_profiles(to_second_warn_profiles, 2)
            to_second_warn_profiles.update(
                nb_deletion_warnings=2, previous_deletion_warning_at=datetime.now()
            )

        # actual deletion
        to_delete = not_deleted_profiles.filter(
            previous_deletion_warning_at__lt=since_second_warning,
            nb_deletion_warnings=2,
        )
        self.stdout.write(f"Deleting {to_delete.count()} users")
        if dry_run:
            self.stdout.write("dry run: no account deleted")
        else:
            for profile in tqdm(to_delete[:10]):
                delete_user(profile.user)

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        self.warn_and_delete(dry_run)
