# encoding: utf-8

"""
Management command to send pending notifications as digests

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-01-24 22:39:27 CEST
"""


from django.contrib.auth import models as auth_models
from django.core.management.base import BaseCommand
from urbanvitaliz.apps.projects import digests
from urbanvitaliz.apps.projects import models as project_models


class Command(BaseCommand):
    help = "Send pending notifications as email digests"

    def handle(self, *args, **options):
        self.send_email_digests()

    def send_email_digests(self):
        # Send project collaborators new recommendations
        for project in project_models.Project.objects.all():
            for user in auth_models.User.objects.filter(email__in=project.emails):
                if digests.send_digests_for_new_recommendations_by_user(user):
                    print(f"Sent new reco digests for {user} on {project.name}")

        # Get all switchtenders
        sw_group = auth_models.Group.objects.get(name="switchtender")

        # Digests for non switchtenders
        for user in auth_models.User.objects.exclude(groups__in=[sw_group]):
            if digests.send_digest_for_non_switchtender_by_user(user):
                print(f"Sent general digest for {user})")

        # Digests for switchtenders
        for user in auth_models.User.objects.filter(groups__in=[sw_group]):
            if digests.send_digests_for_new_sites_by_user(user):
                print(f"Sent new site digests for {user}")

            if digests.send_digest_for_switchtender_by_user(user):
                print(f"Sent general digest for switchtender (to {user})")


# eof
