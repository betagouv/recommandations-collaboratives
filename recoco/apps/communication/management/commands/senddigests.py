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

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.send_email_digests(dry_run=dry_run)

    def send_email_digests(self, dry_run):
        for site in Site.objects.all():
            with settings.SITE_ID.override(site.pk):
                logger.info(f"\n#### Sending digests for site <{site.domain}> ####\n")
                self.send_email_digests_for_site(site, dry_run)

    @staticmethod
    def send_email_digests_for_site(site, dry_run):
        advisor_group = get_group_for_site("advisor", site, create=True)

        # only send emails to active users and those actually linked to the current site
        active_users = auth_models.User.objects.filter(
            is_active=True, profile__sites=site
        )

        # Send reminders (new recommendation + whatsup)
        logger.info("** Sending Project Reminders **")
        for project in project_models.Project.on_site.all():
            digests.send_reminder_digests_by_project(project, dry_run)

        # Send project collaborators new recommendations digest
        logger.info("** Sending new recommendations digests **")
        for (
            project
        ) in project_models.Project.on_site.all():  # FIXME include inactive project?
            for user in project.members.filter(is_active=True):
                if digests.send_digests_for_new_recommendations_by_user(user, dry_run):
                    logger.info(f"Sent new reco digest for {user} on {project.name}")

        # Digests for non switchtenders
        logger.info("** Sending general digests **")  # FIXME include inactive project?
        for user in active_users.exclude(groups__in=[advisor_group]):
            if digests.send_digest_for_non_switchtender_by_user(user, dry_run):
                logger.info(f"Sent general digest for {user}")

        # Digests for switchtenders
        logger.info("** Sending general switchtender digests **")
        # XXX pourquoi groups__in=[] et non groups=advisor_group
        for user in active_users.filter(groups__in=[advisor_group]):
            if digests.send_digests_for_new_sites_by_user(user, dry_run):
                logger.info(f"* Sent new site digest for {user}")

            if digests.send_digest_for_switchtender_by_user(user, dry_run):
                logger.info(f"* Sent general digest for switchtender (to {user})")

    @staticmethod
    def send_test_email_digests_for_project(project, consumes_notifications=True):
        advisor_group = get_group_for_site("advisor", project.site, create=True)

        # only send emails to active users and those actually linked to the current site
        active_users = auth_models.User.objects.filter(
            is_active=True, project_set=project
        )  # todo members and advisors?

        # Send reminders (new recommendation + whatsup)
        logger.info("** Sending Project Reminders **")
        for project in project_models.Project.on_site.all():
            digests.send_reminder_digests_by_project(project)

        # Send project collaborators new recommendations digest
        logger.info("** Sending new recommendations digests **")
        for user in project.members.filter(is_active=True):
            if digests.send_digests_for_new_recommendations_by_user(user):
                logger.info(f"Sent new reco digest for {user} on {project.name}")

        # Digests for non switchtenders
        logger.info("** Sending general digests **")  # FIXME include inactive project?
        for user in active_users.exclude(groups__in=[advisor_group]):
            if digests.send_digest_for_non_switchtender_by_user(user):
                logger.info(f"Sent general digest for {user}")

        # Digests for switchtenders
        logger.info("** Sending general switchtender digests **")
        # XXX pourquoi groups__in=[] et non groups=advisor_group
        for user in active_users.filter(groups__in=[advisor_group]):
            if digests.send_digests_for_new_sites_by_user(user):
                logger.info(f"* Sent new site digest for {user}")

            if digests.send_digest_for_switchtender_by_user(user):
                logger.info(f"* Sent general digest for switchtender (to {user})")


# eof
