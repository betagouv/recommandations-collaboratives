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


class Command(BaseCommand):
    help = "Send pending notifications as email digests"

    def handle(self, *args, **options):
        self.send_email_digests()

    def send_email_digests(self):
        for site in Site.objects.all():
            with settings.SITE_ID.override(site.pk):
                print(f"*** Sending digests for site <{site.domain}> ***")
                self.send_email_digests_for_site(site)

    def send_email_digests_for_site(self, site):
        # Get all switchtenders
        sw_group = auth_models.Group.objects.get(name="switchtender")

        print("** Sending Reminders **")
        # Send reminders
        for user in auth_models.User.objects.filter(is_active=True):
            if digests.send_digests_for_task_reminders_by_user(user):
                print(f"Sent reminder digests for {user}")

        # Send project collaborators new recommendations
        print("** Sending new recommendations digests **")
        for project in project_models.Project.on_site.all():
            for user in project.members.all():
                if digests.send_digests_for_new_recommendations_by_user(user):
                    print(f"Sent new reco digests for {user} on {project.name}")

        # Digests for non switchtenders
        print("** Sending general digests **")
        for user in auth_models.User.objects.exclude(groups__in=[sw_group]):
            if digests.send_digest_for_non_switchtender_by_user(user):
                print(f"Sent general digest for {user})")

        # Digests for switchtenders
        print("** Sending general switchtender digests **")
        for user in auth_models.User.objects.filter(groups__in=[sw_group]):
            if digests.send_digests_for_new_sites_by_user(user):
                print(f"* Sent new site digests for {user}")

            if digests.send_digest_for_switchtender_by_user(user):
                print(f"* Sent general digest for switchtender (to {user})")


# eof
