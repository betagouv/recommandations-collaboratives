# encoding: utf-8

"""
Management command to send pending notifications as digests

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-01-24 22:39:27 CEST
"""


from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from urbanvitaliz.apps.communication import digests
from urbanvitaliz.apps.projects import models as project_models
from urbanvitaliz.utils import get_group_for_site


class Command(BaseCommand):
    help = "Send pending notifications as email digests"

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--dry-run", action="store_true", help="Do not actually send stuff"
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.send_email_digests(dry_run=dry_run)

    def send_email_digests(self, dry_run):
        for site in Site.objects.all():
            with settings.SITE_ID.override(site.pk):
                self.stdout.write("\n")
                self.stdout.write(f"#### Sending digests for site <{site.domain}> ####\n")
                self.stdout.write("\n")
                self.send_email_digests_for_site(site, dry_run)

    def send_email_digests_for_site(self, site, dry_run):
        # FIXME Get all switchtenders BY SITE
        advisor_group = get_group_for_site("advisor", site)
        # sw_group = auth_models.Group.objects.get(name="switchtender")

        # only send emails to active users
        active_users = auth_models.User.objects.filter(is_active=True)

        # Send reminders
        self.stdout.write("** Sending Task Reminders **\n")
        for user in active_users:
            if digests.send_digests_for_task_reminders_by_user(user, dry_run):
                self.stdout.write(f"Sent reminder digest for {user}\n")

        # Send project collaborators new recommendations
        self.stdout.write("** Sending new recommendations digests **\n")
        for project in project_models.Project.on_site.all():
            for user in project.members.filter(is_active=True):
                if digests.send_digests_for_new_recommendations_by_user(user, dry_run):
                    self.stdout.write(f"Sent new reco digest for {user} on {project.name}\n")

        # Digests for non switchtenders
        self.stdout.write("** Sending general digests **\n")
        for user in active_users.exclude(groups__in=[advisor_group]):
            if digests.send_digest_for_non_switchtender_by_user(user, dry_run):
                self.stdout.write(f"Sent general digest for {user}\n")

        # Digests for switchtenders
        self.stdout.write("** Sending general switchtender digests **\n")
        # XXX pourquoi groups__in=[] et non groups=advisor_group
        for user in active_users.filter(groups__in=[advisor_group]):
            if digests.send_digests_for_new_sites_by_user(user, dry_run):
                self.stdout.write(f"* Sent new site digest for {user}\n")

            if digests.send_digest_for_switchtender_by_user(user, dry_run):
                self.stdout.write(f"* Sent general digest for switchtender (to {user})\n")


# eof
