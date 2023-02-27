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
                print("\n")
                print(f"#### Sending digests for site <{site.domain}> ####")
                print("\n")
                self.send_email_digests_for_site(site, dry_run)

    def send_email_digests_for_site(self, site, dry_run):
        # FIXME Get all switchtenders BY SITE
        advisor_group = get_group_for_site("advisor", site)
        # sw_group = auth_models.Group.objects.get(name="switchtender")

        print("** Sending Task Reminders **")
        # Send reminders
        for user in auth_models.User.objects.filter(is_active=True):
            if digests.send_digests_for_task_reminders_by_user(user, dry_run):
                print(f"Sent reminder digests for {user}")

        # Send project collaborators new recommendations
        print("** Sending new recommendations digests **")
        for project in project_models.Project.on_site.all():
            for user in project.members.all():
                if digests.send_digests_for_new_recommendations_by_user(user, dry_run):
                    print(f"Sent new reco digests for {user} on {project.name}")

        # Digests for non switchtenders
        print("** Sending general digests **")
        for user in auth_models.User.objects.exclude(groups__in=[advisor_group]):
            if digests.send_digest_for_non_switchtender_by_user(user, dry_run):
                print(f"Sent general digest for {user})")

        # Digests for switchtenders
        print("** Sending general switchtender digests **")
        for user in auth_models.User.objects.filter(groups__in=[advisor_group]):
            if digests.send_digests_for_new_sites_by_user(user, dry_run):
                print(f"* Sent new site digests for {user}")

            if digests.send_digest_for_switchtender_by_user(user, dry_run):
                print(f"* Sent general digest for switchtender (to {user})")


# eof
