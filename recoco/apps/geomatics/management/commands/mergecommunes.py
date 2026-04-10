# encoding: utf-8

"""
Management command to update projects after commune loading


This command relies on the CSV file listing defunct commune INSEE codes and
their replacement, available from La Poste:

https://datanova.laposte.fr/datasets/laposte-communes-nouvelles
(can be also found on datagouv)

authors: guillaume.libersat@beta.gouv.fr
created: 2026-04-10
"""

import csv
import sys

from django.core.management.base import BaseCommand

from recoco.apps.geomatics import models as geomatics_models
from recoco.apps.projects import models as project_models

OLD_INSEE_COL = "Code INSEE Commune Déléguée (non actif)"
NEW_INSEE_COL = "Code INSEE Commune Nouvelle"


class Command(BaseCommand):
    help = "Update projects referencing merged/defunct commune INSEE codes"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stdin = sys.stdin

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="do not write anything, simulate",
        )

    def handle(self, *args, **options):
        filename = options["filename"]
        dry_run = options["dry_run"]

        updated, warned, not_applicable = merge_communes(
            filename, dry_run, self.stdout, self.stdin
        )

        if dry_run:
            self.stdout.write("[DRY RUN] No changes were made.")
        self.stdout.write(f"Projects updated:              {updated}")
        self.stdout.write(f"Warnings (new commune missing): {warned}")
        self.stdout.write(f"Not applicable (no projects):   {not_applicable}")


def pick_commune(candidates, new_insee, stdout, stdin):
    """Ask the user to pick one commune from a list of candidates."""
    stdout.write(f"Multiple communes found for INSEE {new_insee!r}, please pick one:")
    for i, commune in enumerate(candidates, start=1):
        stdout.write(
            f"  {i}. {commune.name} (postal: {commune.postal}, dept: {commune.department_id})"
        )
    while True:
        stdout.write(f"Pick one [1-{len(candidates)}]: ")
        choice = stdin.readline().strip()
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return candidates[int(choice) - 1]
        stdout.write(f"Invalid choice, enter a number between 1 and {len(candidates)}.")


def merge_communes(filename, dry_run, stdout, stdin):
    mappings = {}
    with open(filename, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            old = row[OLD_INSEE_COL].strip()
            new = row[NEW_INSEE_COL].strip()
            if old and new and old not in mappings:
                mappings[old] = new

    updated = 0
    warned = 0
    not_applicable = 0

    for old_insee, new_insee in mappings.items():
        projects = project_models.Project.objects.filter(commune__insee=old_insee)

        if not projects.exists():
            not_applicable += 1
            continue

        candidates = list(geomatics_models.Commune.objects.filter(insee=new_insee))

        if not candidates:
            stdout.write(
                f"WARNING: new commune INSEE {new_insee!r} not found in DB "
                f"(needed by {projects.count()} project(s) currently on {old_insee!r})"
            )
            warned += 1
            continue

        if len(candidates) == 1:
            new_commune = candidates[0]
        else:
            new_commune = pick_commune(candidates, new_insee, stdout, stdin)

        to_update = projects.exclude(commune=new_commune)
        count = to_update.count()
        old_commune = projects.first().commune
        stdout.write(
            f"{'[DRY RUN] Would update' if dry_run else 'Updating'} "
            f"{count} project(s): {old_insee!r}/{old_commune.postal} ({old_commune.name}) -> "
            f"{new_insee!r}/{new_commune.postal} ({new_commune.name})"
        )

        if not dry_run:
            to_update.update(commune=new_commune)

        updated += count

    return updated, warned, not_applicable


# eof
