# encoding: utf-8

"""
Management command to update projects after commune loading


This command relies on the CSV file listing defunct commune INSEE codes and
their replacement, available from La Poste:

https://datanova.laposte.fr/datasets/laposte-commnouv
(can be also found on datagouv)

authors: guillaume.libersat@beta.gouv.fr
created: 2026-04-10
"""

import csv

from django.core.management.base import BaseCommand

from recoco.apps.geomatics import models as geomatics_models
from recoco.apps.projects import models as project_models

DATE_COL = "Date"

MONTHS = {
    "JANVIER": 1,
    "FÉVRIER": 2,
    "MARS": 3,
    "AVRIL": 4,
    "MAI": 5,
    "JUIN": 6,
    "JUILLET": 7,
    "AOÛT": 8,
    "SEPTEMBRE": 9,
    "OCTOBRE": 10,
    "NOVEMBRE": 11,
    "DÉCEMBRE": 12,
}

OLD_INSEE_COL = "Code INSEE Commune Déléguée (non actif)"
NEW_INSEE_COL = "Code INSEE Commune Nouvelle"
NEW_NAME_COL = "Nom Commune Nouvelle Siège"
NEW_POSTAL_COL = "Adresse 2016 - L6 Code Postal"


class Command(BaseCommand):
    help = "Update communes and projects after commune merges"

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

        created, renamed, updated, deleted, warned = merge_communes(
            filename, dry_run, self.stdout
        )

        if dry_run:
            self.stdout.write("[DRY RUN] No changes were made.")
        self.stdout.write(f"Communes created:  {created}")
        self.stdout.write(f"Communes renamed:  {renamed}")
        self.stdout.write(f"Communes deleted:  {deleted}")
        self.stdout.write(f"Projects updated:  {updated}")
        self.stdout.write(f"Warnings:          {warned}")


def parse_date(date_str):
    """Return a (year, month) tuple for sorting; unknown dates sort last."""
    parts = date_str.strip().upper().split()
    if len(parts) == 2:
        month = MONTHS.get(parts[0])
        try:
            year = int(parts[1])
        except ValueError:
            year = None
        if month and year:
            return (year, month)
    return (9999, 99)


def dept_code_from_insee(insee):
    """Derive department code from a 5-char INSEE commune code."""
    if insee[:2] in ("2A", "2B"):
        return insee[:2]
    if insee.startswith("97"):
        return insee[:3]
    return insee[:2]


def merge_communes(filename, dry_run, stdout):
    mappings = {}  # old_insee -> (new_insee, new_postal, new_name)
    with open(filename, newline="", encoding="utf-8") as f:
        rows = sorted(csv.DictReader(f), key=lambda r: parse_date(r[DATE_COL]))
    for row in rows:
        old = row[OLD_INSEE_COL].strip()
        new = row[NEW_INSEE_COL].strip()
        postal = row[NEW_POSTAL_COL].strip()
        name = row[NEW_NAME_COL].strip().rstrip(" *")
        if old and new and old not in mappings:
            mappings[old] = (new, postal, name)

    created = 0
    renamed = 0
    updated = 0
    deleted = 0
    warned = 0

    # Pass 1: ensure new Commune records exist with the correct name
    # create or rename, depending on the existing data
    seen_new_insee = set()
    for old_insee, (new_insee, new_postal, new_name) in mappings.items():
        if new_insee in seen_new_insee:
            continue
        seen_new_insee.add(new_insee)

        if not new_postal:
            old_commune = geomatics_models.Commune.objects.filter(
                insee=old_insee
            ).first()
            if old_commune:
                new_postal = old_commune.postal
                stdout.write(
                    f"No postal for {new_insee}, falling back to old commune "
                    f"{old_insee} postal {new_postal}"
                )
            else:
                stdout.write(
                    f"WARNING: no postal code for new commune {new_insee} ({new_name}) "
                    f"and old commune {old_insee} not found, skipping"
                )
                warned += 1
                continue

        dept_code = dept_code_from_insee(new_insee)
        try:
            dept = geomatics_models.Department.objects.get(code=dept_code)
        except geomatics_models.Department.DoesNotExist:
            stdout.write(
                f"WARNING: department {dept_code} not found for commune {new_insee}, skipping"
            )
            warned += 1
            continue

        existing = geomatics_models.Commune.objects.filter(
            insee=new_insee, postal=new_postal
        ).first()
        if existing:
            if existing.name != new_name:
                stdout.write(
                    f"{'[DRY RUN] Would rename' if dry_run else 'Renaming'} "
                    f"Commune {new_insee}/{new_postal}: {existing.name} -> {new_name}"
                )
                if not dry_run:
                    existing.name = new_name
                    existing.save(update_fields=["name"])
                renamed += 1
        else:
            stdout.write(
                f"{'[DRY RUN] Would create' if dry_run else 'Creating'} "
                f"Commune {new_insee}/{new_postal} ({new_name})"
            )
            if not dry_run:
                geomatics_models.Commune.objects.create(
                    insee=new_insee,
                    postal=new_postal,
                    name=new_name,
                    department=dept,
                )
            created += 1

    # Pass 2: update project commune references from old INSEE to new
    for old_insee, (new_insee, _, _) in mappings.items():
        projects = project_models.Project.objects.filter(commune__insee=old_insee)
        if not projects.exists():
            continue

        new_commune = geomatics_models.Commune.objects.filter(insee=new_insee).first()
        if not new_commune:
            stdout.write(
                f"WARNING: new commune {new_insee} not found, cannot update projects on {old_insee}"
            )
            warned += 1
            continue

        to_update = projects.exclude(commune=new_commune)
        count = to_update.count()
        if count:
            old_commune = to_update.first().commune
            stdout.write(
                f"{'[DRY RUN] Would update' if dry_run else 'Updating'} "
                f"{count} project(s): {old_insee}/{old_commune.postal} ({old_commune.name}) -> "
                f"{new_insee}/{new_commune.postal} ({new_commune.name})"
            )
            if not dry_run:
                to_update.update(commune=new_commune)
            updated += count

    # Pass 3: delete old communes (no longer referenced by any project)
    for old_insee, (new_insee, _, _) in mappings.items():
        # Prevent from deleting Communes that were merged with themselves
        if old_insee == new_insee:
            continue
        for old_commune in geomatics_models.Commune.objects.filter(insee=old_insee):
            if not project_models.Project.objects.filter(commune=old_commune).exists():
                stdout.write(
                    f"{'[DRY RUN] Would delete' if dry_run else 'Deleting'} "
                    f"orphan Commune {old_insee}/{old_commune.postal} ({old_commune.name})"
                )
                if not dry_run:
                    old_commune.delete()
                deleted += 1

    return created, renamed, updated, deleted, warned


# eof
