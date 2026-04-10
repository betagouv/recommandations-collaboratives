# encoding: utf-8

"""
Management command to import communes into geomatics


This command relies on the csv file with commune / departement / region data
available from the following url:

https://www.data.gouv.fr/fr/datasets/communes-de-france-base-des-codes-postaux/


authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-07-13 09:08:25 CEST
"""

import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from recoco.apps.geomatics import models


class Command(BaseCommand):
    help = "Import France communes/department/region from given CSV file"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        filename = options["filename"]
        created, existing, only_in_db = load_communes_from_csv(filename)
        self.stdout.write(f"Newly created:    {created}")
        self.stdout.write(f"Already existing: {existing}")
        self.stdout.write(f"Only in DB:       {only_in_db}")


@transaction.atomic
def load_communes_from_csv(filename):
    csv_insee_codes = set()
    created_count = 0
    existing_count = 0

    with open(filename, newline="", encoding="utf-8") as the_file:
        reader = csv.DictReader(the_file)
        for row in reader:
            insee = row["code_insee"]
            csv_insee_codes.add(insee)
            _, was_created = load_commune(row)
            if was_created:
                created_count += 1
            else:
                existing_count += 1

    only_in_db = models.Commune.objects.exclude(insee__in=csv_insee_codes).count()

    return created_count, existing_count, only_in_db


def load_commune(row):
    """Create commune department region from row if unknown"""
    region = get_region(row["reg_code"], row["reg_nom"])
    department = get_department(region, row["dep_code"], row["dep_nom"])
    commune, created = models.Commune.objects.get_or_create(
        department=department,
        insee=row["code_insee"],
        postal=row.get("code_postal", "") or "",
        defaults={
            "name": row["nom_standard"],
            "latitude": float(row["latitude_centre"])
            if row.get("latitude_centre")
            else 0.0,
            "longitude": float(row["longitude_centre"])
            if row.get("longitude_centre")
            else 0.0,
        },
    )
    return commune, created


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
        code=code, defaults={"name": name}
    )
    return departement


# eof
