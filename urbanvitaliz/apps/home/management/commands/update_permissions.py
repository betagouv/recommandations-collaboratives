# encoding: utf-8

"""
Command to update permissions for User and Groups

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-02-21 18:57:48 CET
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


from urbanvitaliz.utils import get_group_for_site
from urbanvitaliz.apps.home.models import SITE_GROUP_PERMISSIONS
from guardian.shortcuts import assign_perm


class Command(BaseCommand):
    help = "Update permissions for User and Groups"

    def handle(self, *args, **options):
        # Per site permissions for Group
        for site in Site.objects.all():
            print("site:", site)
            for group_name, permissions in SITE_GROUP_PERMISSIONS.items():
                group = get_group_for_site(group_name, site)
                for perm_name in permissions:
                    print("group:", group, "perm:", perm_name)
                    assign_perm(perm_name, group, obj=site)

        # --- ADMIN --#
        # Survey
        for site in Site.objects.all():
            group = get_group_for_site("admin", site)
            # assign_perm("survey.manage_surveys", group, obj=site)
