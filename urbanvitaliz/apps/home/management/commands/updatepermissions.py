# encoding: utf-8

"""
Command to update permissions of various groups in the application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-11-15 18:57:48 CET
"""

from django.core.management.base import BaseCommand

from django.contrib.auth import models as auth


class Command(BaseCommand):
    help = "Update permissions associated w/ groups in uv"

    def handle(self, *args, **options):
        g = auth.Group.objects.get(name="switchtender")
        p = auth.Permission.objects.get(codename="can_administrate_project")
        g.permissions.add(p)
        print("switchtender permissions:", g.permissions.all())


# eof
