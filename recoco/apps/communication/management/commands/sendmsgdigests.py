import logging

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db.models import Q

from recoco.apps.communication import digests
from recoco.apps.projects import models as project_models

logger = logging.getLogger("main")


class Command(BaseCommand):
    help = "Send pending notifications as email digests"

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--dry-run", action="store_true", help="Do not actually send stuff"
        )
        parser.add_argument(
            "-u",
            "--user-id",
            action="store",
            help="specific user id to whom send digests",
            type=int,
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        user_id = options["user_id"]

        self.send_msg_email_digests(dry_run=dry_run, user_id=user_id)

    def send_msg_email_digests(self, dry_run, user_id):
        for site in Site.objects.all():
            with settings.SITE_ID.override(site.pk):
                logger.info(f"\n#### Sending digests for site <{site.domain}> ####\n")
                self.send_msg_email_digests_for_site(site, dry_run, user_id)

    def send_msg_email_digests_for_site(self, site, dry_run, user_id):
        # only send emails to active users and those actually linked to the current site
        user_qs = auth_models.User.objects

        if user_id is not None:
            user_qs = user_qs.filter(pk=user_id)

            logger.info(f"Specific user {user_qs.first().email} required")
        else:
            user_qs = user_qs.filter(is_active=True, profile__sites=site)

        # Message digests
        logger.info("** Sending message digests **")
        for project in project_models.Project.on_site.all():
            members_or_switchtenders = Q(projectmember__project=project) | Q(
                projects_switchtended_per_site__project=project
            )
            for user in user_qs.filter(members_or_switchtenders).distinct():
                digests.send_msg_digest_by_user_and_project(
                    project, user, site, dry_run
                )


# eof
