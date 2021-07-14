# encoding: utf-8

"""
Management command to import communes into geomatics


This command relies on the csv file with commune / departement / region data
available from the following url:

https://www.data.gouv.fr/fr/datasets/r/dbe8a621-a9c4-4bc3-9cae-be1699c5ff25


authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-07-13 09:08:25 CEST
"""

import csv

from django.db import transaction

from django.core.management.base import BaseCommand

from urbanvitaliz.apps.geomatics import models


class Command(BaseCommand):
    help = "Import France communes/department/region from given CSV file"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        filename = options["filename"]
        load_communes_from_csv(filename)


@transaction.atomic
def load_communes_from_csv(filename):
    with open(filename) as the_file:
        reader = csv.DictReader(the_file)
        for row in reader:
            load_commune(row)


def load_commune(row):
    """Create commune department region from row if unknown"""
    region = get_region(row["code_region"], row["nom_region"])
    department = get_department(region, row["code_departement"], row["nom_departement"])
    commune, _ = models.Commune.objects.get_or_create(
        department=department,
        insee=row["code_commune_INSEE"],
        postal=row["code_postal"],
        defaults={
            "name": row["nom_commune_postal"],
            "latitude": row["latitude"] or 0.0,
            "longitude": row["longitude"] or 0.0,
        },
    )
    return commune


def memoize(function):
    """Memoize departments and regions to reduce db queries"""
    memory = {}

    def wrapper(*args, **kwargs):
        if args not in memory:
            memory[args] = function(*args)
        return memory[args]

    return wrapper


@memoize
def get_region(code, name):
    region, _ = models.Region.objects.get_or_create(code=code, defaults={"name": name})
    return region


@memoize
def get_department(region, code, name):
    departement, _ = models.Department.objects.get_or_create(
        region=region, code=code, defaults={"name": name}
    )
    return departement


# eof
