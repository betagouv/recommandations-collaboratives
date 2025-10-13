# encoding: utf-8

"""
Management command to send pending notifications as digests

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-01-24 22:39:27 CEST
"""

import logging

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from recoco.apps.communication import digests
from recoco.apps.projects import models as project_models
from recoco.utils import get_group_for_site

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
            help="Do not actually send stuff",
            type=int,
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        user_id = options["user_id"]

        self.send_email_digests(dry_run=dry_run, user_id=user_id)

    def send_email_digests(self, dry_run, user_id):
        for site in Site.objects.all():
            with settings.SITE_ID.override(site.pk):
                logger.info(f"\n#### Sending digests for site <{site.domain}> ####\n")
                self.send_email_digests_for_site(site, dry_run, user_id)

    def send_email_digests_for_site(self, site, dry_run, user_id):
        advisor_group = get_group_for_site("advisor", site, create=True)

        # only send emails to active users and those actually linked to the current site
        user_qs = auth_models.User.objects

        if user_id is not None:
            user_qs = user_qs.filter(pk=user_id)

            logger.info("Specific user required. Ignoring whatsup by project digests")
        else:
            user_qs = user_qs.filter(is_active=True, profile__sites=site)

            # Send reminders (new recommendation + whatsup)
            logger.info("** Sending Project Reminders **")
            for project in project_models.Project.on_site.all():
                digests.send_reminder_digests_by_project(project, dry_run)

            # Send project collaborators new recommendations digest
            logger.info("** Sending new recommendations digests **")
            for project in (
                project_models.Project.on_site.all()
            ):  # FIXME include inactive project?
                for user in project.members.filter(is_active=True):
                    if digests.send_digests_for_new_recommendations_by_user(
                        user, dry_run
                    ):
                        logger.info(
                            f"Sent new reco digest for {user} on {project.name}"
                        )

        # Message digests
        logger.info("** Sending message digests **")  # FIXME include inactive project?
        for project in project_models.Project.on_site.all():
            for user in user_qs.intersection(
                project.members.union(project.switchtenders)
            ):
                digests.send_msg_digest_by_user_and_project(project, user, dry_run)

        # Digests for non switchtenders
        logger.info("** Sending general digests **")  # FIXME include inactive project?
        for user in user_qs.exclude(groups__in=[advisor_group]):
            if digests.send_digest_for_non_switchtender_by_user(user, dry_run):
                logger.info(f"Sent general digest for {user}")

        # Digests for switchtenders
        logger.info("** Sending general switchtender digests **")
        # XXX pourquoi groups__in=[] et non groups=advisor_group
        for user in user_qs.filter(groups__in=[advisor_group]):
            if digests.send_digests_for_new_sites_by_user(user, dry_run):
                logger.info(f"* Sent new site digest for {user}")

            if digests.send_digest_for_switchtender_by_user(user, dry_run):
                logger.info(f"* Sent general digest for switchtender (to {user})")


# eof
