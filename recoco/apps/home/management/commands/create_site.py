from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from guardian.shortcuts import assign_perm

from recoco.apps.home import models
from recoco.apps.survey import models as survey_models
from recoco.utils import get_group_for_site


class Command(BaseCommand):
    help = "Create a site and the few things needed"

    def add_arguments(self, parser):
        parser.add_argument("-n", "--name", type=str, help="The name of the site", required=True)
        parser.add_argument("-d", "--domain", type=str, help="The domain of the new site without protocol (Ex: example.com)", required=True)
        parser.add_argument("-se", "--sender-email", type=str, help="The email address used as the sender for emails sent from the site", required=True)
        parser.add_argument("-sn", "--sender-name", type=str, help="The name used as the sender for emails sent from the site", required=True)
        parser.add_argument("-cr", "--contact-form-recipient", type=str, help="The email address where contact form messages should be sent", required=True)
        parser.add_argument("-la", "--legal-address", type=str, help="The legal address of the company or entity that owns the site",)
        # TODO: add email logo

    def handle(self, *args, **options):
        name = options["name"]
        domain = options["domain"]
        sender_email = options["sender_email"]
        sender_name = options["sender_name"]
        contact_form_recipient = options["contact_form_recipient"]
        legal_address = options["legal_address"]

        if Site.objects.filter(domain=domain).count():
            raise CommandError(f"The domain {domain} already used")

        with transaction.atomic():
            self.stdout.write("Site creation starts..")
            site = Site.objects.create(name=name, domain=domain)

            self.stdout.write("Create default project survey..")
            survey, created = survey_models.Survey.objects.get_or_create(
                site=site,
                defaults={
                    "name": f"Questionnaire par défaut de {name}",
                },
            )

            if created:
                # if we just created the survey, create initial sample questions
                question_set = survey_models.QuestionSet.objects.create(
                    survey=survey, heading="Thématique d'exemple"
                )
                survey_models.Question.objects.create(
                    question_set=question_set, text="Ceci est une question exemple"
                )

            self.stdout.write("Create site configuration..")
            models.SiteConfiguration.objects.create(
                site=site,
                project_survey=survey,
                sender_email=sender_email,
                sender_name=sender_name,
                contact_form_recipient=contact_form_recipient,
                legal_address=legal_address,
            )

            self.stdout.write("Create group and permissions..")
            with settings.SITE_ID.override(site.pk):
                for group_name, permissions in models.SITE_GROUP_PERMISSIONS.items():
                    group = get_group_for_site(group_name, site, create=True)
                    for perm_name in permissions:
                        assign_perm(perm_name, group, obj=site)
                        
            self.stdout.write(self.style.SUCCESS(f"The site {name} has been created successfully"))

            if not domain.endswith(".recoconseil.fr"):
                self.stdout.write(self.style.SUCCESS(f"The domain {domain} requires additional configuration on the server !"))

