# encoding: utf-8

"""
Command to update permissions for User and Groups

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-02-21 18:57:48 CET
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from guardian.shortcuts import assign_perm

from recoco.apps.home.models import SITE_GROUP_PERMISSIONS
from recoco.apps.invites.models import Invite
from recoco.apps.projects.models import Project, ProjectSwitchtender
from recoco.apps.projects.utils import (
    assign_advisor,
    assign_collaborator_permissions,
    assign_observer,
)
from recoco.utils import get_group_for_site


def assign_user_permissions_by_projects():
    """Per project permission for user."""
    for project in Project.objects.all():
        print("Updating perms for project:", project.name)
        for site in project.sites.all():
            print("\t* Updating permissions for collaborators...")
            with settings.SITE_ID.override(site.id):
                for membership in project.projectmember_set.all():
                    assign_collaborator_permissions(membership.member, project)

                print("\t* Updating permissions for advisors/observers...")
                print(f"\t== On site {site} ==")

                for project_advisor in ProjectSwitchtender.objects.filter(
                    project=project
                ):
                    if project_advisor.is_observer:
                        print(
                            "\t\t* OBSERVER:",
                            project_advisor.switchtender,
                        )
                        assign_observer(
                            project_advisor.switchtender,
                            project,
                            site=project_advisor.site,
                        )
                    else:
                        print(
                            "\t\t* ADVISOR:",
                            project_advisor.switchtender,
                        )
                        assign_advisor(
                            project_advisor.switchtender,
                            project,
                            site=project_advisor.site,
                        )


def assign_group_permissions_by_sites():
    """Per site permissions for Group."""
    for site in Site.objects.all():
        print("site:", site)
        with settings.SITE_ID.override(site.id):
            for group_name, permissions in SITE_GROUP_PERMISSIONS.items():
                group = get_group_for_site(group_name, site, create=True)
                for perm_name in permissions:
                    print("group:", group, "perm:", perm_name, "site:", site.name)
                    assign_perm(perm_name, group, obj=site)

            # assign site perms to advisor invites, as they don't belong to the advisor group
            for invite in Invite.objects.filter(
                site=site,
                role="SWITCHTENDER",
                accepted_on__isnull=False,
            ):
                invited_user = User.objects.filter(email=invite.email).first()
                if not invited_user:
                    continue
                for perm_name in SITE_GROUP_PERMISSIONS.get("advisor"):
                    print(
                        "invited user:",
                        invited_user.email,
                        "perm:",
                        perm_name,
                        "site:",
                        site.name,
                    )
                    assign_perm(perm_name, invited_user, obj=site)


class Command(BaseCommand):
    help = "Update permissions for User and Groups"

    def handle(self, *args, **options):
        assign_group_permissions_by_sites()
        assign_user_permissions_by_projects()


# eof
