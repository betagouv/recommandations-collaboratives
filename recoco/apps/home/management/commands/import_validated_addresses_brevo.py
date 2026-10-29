import csv

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Imports data about confirmed email addresses"

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            help="Do not actually save confirmations",
        )
        parser.add_argument(
            "--path",
            help="Path to export csv from brevo. DL from brevo in transactional/email/logs, "
            "select desired date filter and 'Cliqué' event, then 'Télécharger le fichier csv'",
        )

    def import_from_brevo(self, path, dry_run):
        email_addresses_to_validate = []
        email_addresses_to_add = []
        email_user_to_update = []
        address_no_user = set()
        already_valid_count = 0
        link_ignored_count = 0
        seen_emails = set()
        with open(path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["st_text"] != "Cliqué":
                    continue
                if "sesame=" not in row["link"] and "invite" not in row["link"]:
                    link_ignored_count += 1
                    continue

                email = row["email"]

                if email in seen_emails:  # many rows same email so skipping
                    continue

                seen_emails.add(email)
                if not (
                    user := User.objects.filter(email=email).first()
                ):  # no user found for this email - skipping
                    address_no_user.add(email)
                    continue

                count_same = EmailAddress.objects.filter(email=email, user=user).count()
                if count_same == 1:
                    email_address = EmailAddress.objects.get(email=email)
                    if email_address.verified:
                        already_valid_count += 1
                        continue
                    email_address.verified = True
                    email_addresses_to_validate.append(email_address)
                elif count_same == 0:
                    count_diff = EmailAddress.objects.filter(user=user).count()
                    if count_diff == 0:
                        email_addresses_to_add.append(
                            EmailAddress(
                                email=email, verified=True, primary=True, user=user
                            )
                        )
                    else:
                        email_address = EmailAddress.objects.get(user=user)
                        email_user_to_update.append((email_address, user))

        if email_user_to_update:
            self.stdout.write(
                "Addresses that should be manually updated to account for manual changes. Ignored by the script",
            )
            self.stdout.write("user_id, user__email, address__email, address_id")
            for email_address, user in email_user_to_update:
                self.stdout.write(
                    f"{user.id}, {user.email}, {email_address.email}, {email_address.id}"
                )

        if dry_run:
            self.stdout.write(
                "DRY RUN - all stats are speculative, no change was operated in db"
            )
        else:
            EmailAddress.objects.bulk_update(email_addresses_to_validate, ["verified"])
            EmailAddress.objects.bulk_create(email_addresses_to_add)

        self.stdout.write(
            f"{len(email_addresses_to_validate) + len(email_addresses_to_add)} validated addresses"
        )
        self.stdout.write(
            f"{len(address_no_user)} addresses skipped because no user was found"
        )
        self.stdout.write(f"{already_valid_count} addresses already validated")
        self.stdout.write(
            f"{link_ignored_count} rows skipped because the clicked link was not related to authentification"
        )
        self.stdout.write(f"{len(seen_emails)} emails treated")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        path = options["path"]
        self.import_from_brevo(path, dry_run)
