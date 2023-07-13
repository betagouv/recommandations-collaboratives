# encoding: utf-8

"""
Script to update the duplicated organizations


To be updated:

- project
- contact

Provided CSV files has 5 columns:

- id         current org id
- name       current org name
- new_id     org id to replace current one (if present)
- new_name   new name of current org (if present)
- to_delete  delete current org (if present)

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-10 13:36:20 CEST
"""

import csv

from django.core.management.base import BaseCommand

from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.home import models as home_models


class Command(BaseCommand):
    help = "Cleanup organizations according to given csv file"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        filename = options["filename"]
        process_file(filename)


def process_file(filename: str):
    """Process given csv file containing organization updates"""
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)  # skip header line
        process_lines(reader)


def process_lines(lines):
    """Process all the given lines"""
    for line in lines:
        process_line(line)


def process_line(line):
    """Process the given line"""
    id, name, new_id, new_name, to_delete = line

    # use a queryset to perform update without multiple requests
    org = addressbook_models.Organization.objects.filter(id=id)

    if new_name:  # update organization name
        org.update(name=new_name)

    if new_id:  # update related objects to new organization
        home_models.UserProfile.objects.filter(organization_id=id).update(
            organization_id=new_id
        )
        addressbook_models.Contact.objects.filter(organization_id=id).update(
            organization_id=new_id
        )

    if new_id or to_delete:  # delete useless organization
        org.delete()


# eof
