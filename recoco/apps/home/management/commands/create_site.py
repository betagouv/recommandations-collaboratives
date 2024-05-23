from django.core.management.base import BaseCommand, CommandError

from recoco.apps.home import utils


class Command(BaseCommand):
    help = "Create a site and the few things needed"

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--name", type=str, help="The name of the site", required=True
        )
        parser.add_argument(
            "-d",
            "--domain",
            type=str,
            help="The domain of the new site without protocol (Ex: example.com)",
            required=True,
        )
        parser.add_argument(
            "-se",
            "--sender-email",
            type=str,
            help="The email address used as the sender for emails sent from the site",
            required=True,
        )
        parser.add_argument(
            "-sn",
            "--sender-name",
            type=str,
            help="The name used as the sender for emails sent from the site",
            required=True,
        )
        parser.add_argument(
            "-cr",
            "--contact-form-recipient",
            type=str,
            help="The email address where contact form messages should be sent",
            required=True,
        )
        parser.add_argument(
            "-la",
            "--legal-address",
            type=str,
            help="The legal address of the company or entity that owns the site",
        )
        # TODO: add email logo

    def handle(self, *args, **options):
        name = options["name"]
        domain = options["domain"]
        sender_email = options["sender_email"]
        sender_name = options["sender_name"]
        contact_form_recipient = options["contact_form_recipient"]
        legal_address = options["legal_address"]

        try:
            site = utils.make_new_site(
                name,
                domain,
                sender_email,
                sender_name,
                contact_form_recipient,
                legal_address,
            )

            if site:
                self.stdout.write(
                    self.style.SUCCESS(f"The site {name} has been created successfully")
                )

                if not domain.endswith(".recoconseil.fr"):
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"The domain {domain} requires additional configuration on the server !"
                        )
                    )

        except Exception as e:
            raise CommandError(e)
