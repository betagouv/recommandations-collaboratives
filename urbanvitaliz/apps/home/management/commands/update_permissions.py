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
from urbanvitaliz.apps.projects.models import Project, ProjectSwitchtender
from urbanvitaliz.apps.projects.utils import (
    assign_collaborator,
    assign_observer,
    assign_advisor,
)
from guardian.shortcuts import assign_perm


def assign_user_permissions_by_projects():
    """Per project permission for user"""
    for project in Project.objects.all():
        for membership in project.projectmember_set.all():
            assign_collaborator(
                membership.member, project, is_owner=membership.is_owner
            )

        for project_advisor in ProjectSwitchtender.objects.filter(project=project):
            if project_advisor.is_observer:
                assign_observer(
                    project_advisor.switchtender, project, site=project_advisor.site
                )
            else:
                assign_advisor(
                    project_advisor.switchtender, project, site=project_advisor.site
                )


def assign_group_permissions_by_sites():
    """Per site permissions for Group"""
    for site in Site.objects.all():
        print("site:", site)
        for group_name, permissions in SITE_GROUP_PERMISSIONS.items():
            group = get_group_for_site(group_name, site)
            for perm_name in permissions:
                print("group:", group, "perm:", perm_name)
                assign_perm(perm_name, group, obj=site)


class Command(BaseCommand):
    help = "Update permissions for User and Groups"

    def handle(self, *args, **options):
        assign_group_permissions_by_sites()
        assign_user_permissions_by_projects()


# eof
