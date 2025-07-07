#!/usr/bin/env python

import csv

from django.contrib.sites.models import Site
from django.utils import timezone

from recoco.apps.geomatics.models import Department
from recoco.apps.resources.models import Category, Resource


def import_resources_from_csv(csv_path):
    """
    Imports resources from a CSV file into the Resource model.

    :param csv_path: Path to the CSV file
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if not row["TITRE"]:
                print(f"XX Skipped {row}")
                continue  # Skip empty rows

            # Get or create category
            category_name = row["CATEGORY"].strip()
            category = None
            if category_name:
                category, _ = Category.objects.get_or_create(
                    name=category_name, sites=Site.objects.get_current()
                )
                category.sites.add(Site.objects.get_current())

            # Handle departments (if you have logic to map from name to instance)
            departments = []
            location = row["LOCALISATION"].strip()
            if location:
                location = location.lower()

                if location == "métropole":
                    departments = Department.objects.exclude(
                        code__in=[
                            "971",
                            "973",
                            "972",
                            "976",
                            "974",
                            "986",
                            "987",
                            "978",
                            "977",
                            "975",
                        ]
                    )

            # Construct content from multiple columns
            extra_blocks = []
            for key in [
                "Accompagnement par un opérateur",
                "Durée type de l'accompagnement",
                "Référent à contacter",
                "Coût",
                "Aide publique ?",
                "Page web dédiée",
                "REX associés",
            ]:
                value = row.get(key, "").strip()
                if value:
                    extra_blocks.append(f"### {key}\n\n{value}\n\n")
            content_extra = "\n\n" + "\n".join(extra_blocks)

            # Create resource
            resource = Resource.objects.create(
                title=row["TITRE"].strip(),
                subtitle=row.get("SOUS-TITRE", "").strip(),
                summary=row.get("RESUME", "").strip(),
                content=(
                    f"## 🚀 L’APPUI PROPOSÉ\n\n{row.get('TEXTE DE LA RESSOURCE', '')}\n\n"
                    + content_extra
                ).strip(),
                category=category,
                status=Resource.PUBLISHED,
                created_on=timezone.now(),
                updated_on=timezone.now(),
                site_origin=Site.objects.get_current(),
            )
            resource.sites.add(Site.objects.get_current())
            if departments:
                resource.departments.set(departments)

            count += 1
        print(f"✅ Imported {count} resources")
