# encoding: utf-8

"""
Management command to set project inactive if no users have logged in for
a long time

authors: sebastien.reuiller@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2024-01-22 16:39:27 CEST
"""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Max, Q
from django.utils import timezone

from recoco.apps.projects import models as project_models

logger = logging.getLogger("main")


class Command(BaseCommand):
    help = "Update inactive since"

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--dry-run", action="store_true", help="Do not actually send stuff"
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # FIXME Make inactivity time configurable from a SiteConfiguration. Set as 12
        # months by default.
        inactivity_period = 30 * 12  # in days ~= 12months
        twelve_months_ago = timezone.now() - timedelta(days=inactivity_period)

        old_projects = (
            project_models.Project.objects.filter(inactive_since=None)
            .exclude(created_on__gt=twelve_months_ago)
            .prefetch_related("members")
            .annotate(last_log=Max("members__last_login"))
            .filter(Q(last_log__lte=twelve_months_ago) | Q(last_log=None))
            .filter(
                Q(last_manual_reactivation__lte=twelve_months_ago)
                | Q(last_manual_reactivation=None)
            )
        )

        if dry_run:
            logger.info(f"** Would set {old_projects.count()} projects as inactive **")
        else:
            logger.info(f"** Setting {old_projects.count()} projects as inactive **")

        for project in old_projects:
            if not project.last_log:
                project.last_log = project.created_on

            project.inactive_since = project.last_log + timedelta(
                days=inactivity_period
            )
            project.inactive_reason = (
                "Pas de connexion de membres de "
                "la collectivité dans les 12 mois"  # XXX hardcoded
            )

            logger.info(
                f"{project.name} ({project.id}) ; "
                f"last_login={project.last_log.strftime('%Y-%m-%d')} -> "
                f"set inactive@{project.inactive_since.strftime('%Y-%m-%d')}"
            )

            if not dry_run:
                project.save()
