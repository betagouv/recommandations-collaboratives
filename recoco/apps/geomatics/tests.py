# encoding: utf-8

"""
Testing geomatics application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-10-11 19:06:54 CEST
"""

import io
from unittest.mock import mock_open, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from model_bakery import baker

from recoco.apps.geomatics.management.commands.loadcommunes import (
    get_department,
    get_region,
)
from recoco.apps.geomatics.management.commands.mergecommunes import merge_communes
from recoco.apps.projects import models as project_models

from . import models


@pytest.fixture(autouse=True)
def clear_lru_caches():
    get_region.cache_clear()
    get_department.cache_clear()


##### Loading ######
def test_load_communes_fails_when_no_file_provided():
    with pytest.raises(CommandError):
        call_command("loadcommunes")


@pytest.mark.django_db
def test_load_empty_file_do_not_create_anything():
    with patch("builtins.open", mock_open(read_data="")):
        call_command("loadcommunes", "empty.csv")
    assert models.Region.objects.count() == 0
    assert models.Department.objects.count() == 0
    assert models.Commune.objects.count() == 0


@pytest.mark.django_db
def test_load_file_create_region_department_and_commune():
    with patch("builtins.open", mock_open(read_data=CSV)):
        call_command("loadcommunes", "communes.csv")
    region = models.Region.objects.all()[0]
    assert region.name == "Auvergne-Rhône-Alpes"
    assert region.code == "84"
    department = models.Department.objects.all()[0]
    assert department.name == "Ain"
    assert department.code == "01"
    commune = models.Commune.objects.all()[0]
    assert commune.name == "L'Abergement-Clémenciat"
    assert commune.insee == "01001"
    assert commune.postal == "01400"
    assert commune.latitude == 46.153
    assert commune.longitude == 4.926


@pytest.mark.django_db
def test_load_file_existing_commune_not_duplicated():
    with patch("builtins.open", mock_open(read_data=CSV)):
        call_command("loadcommunes", "communes.csv")
        call_command("loadcommunes", "communes.csv")
    assert models.Commune.objects.count() == 1


####### Commune merging ########

CSV = """,code_insee,nom_standard,code_postal,dep_code,dep_nom,reg_code,reg_nom,latitude_centre,longitude_centre
0,01001,L'Abergement-Clémenciat,01400,01,Ain,84,Auvergne-Rhône-Alpes,46.153,4.926
"""

MERGE_CSV_HEADER = (
    "Date,Code INSEE Commune Nouvelle,Nom Commune Nouvelle Siège,"
    "Code INSEE Commune Déléguée (non actif),Nom Commune Déléguée,"
    "Adresse 2016 - L6 Code Postal\n"
)


def make_merge_csv(*rows):
    """Build a merge CSV string from (old_insee, new_insee, new_postal) tuples."""
    lines = MERGE_CSV_HEADER
    for old, new, postal in rows:
        lines += f"AVRIL 2016,{new},Commune Nouvelle,{old},Commune Déléguée,{postal}\n"
    return lines


@pytest.fixture
def dept_39(db):
    region = baker.make(models.Region, code="84", name="Bourgogne-Franche-Comté")
    return baker.make(models.Department, code="39", name="Jura", region=region)


# --- Pass 1: create / rename new communes ---


@pytest.mark.django_db
def test_merge_pass1_creates_new_commune(dept_39):
    baker.make(models.Commune, insee="39023", postal="39190", department=dept_39)
    csv_data = make_merge_csv(("39023", "39378", "39320"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        created, renamed, updated, deleted, warned = merge_communes(
            "merge.csv", False, io.StringIO()
        )
    assert created == 1
    assert models.Commune.objects.filter(insee="39378", postal="39320").exists()


@pytest.mark.django_db
def test_merge_pass1_renames_existing_commune_when_name_differs(dept_39):
    baker.make(
        models.Commune,
        insee="39378",
        postal="39320",
        name="Ancien Nom",
        department=dept_39,
    )
    csv_data = make_merge_csv(("39023", "39378", "39320"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        created, renamed, updated, deleted, warned = merge_communes(
            "merge.csv", False, io.StringIO()
        )
    assert renamed == 1
    assert (
        models.Commune.objects.get(insee="39378", postal="39320").name
        == "Commune Nouvelle"
    )


@pytest.mark.django_db
def test_merge_pass1_falls_back_to_old_commune_postal(dept_39):
    baker.make(models.Commune, insee="39023", postal="39190", department=dept_39)
    csv_data = make_merge_csv(("39023", "39378", ""))  # no postal in CSV
    with patch("builtins.open", mock_open(read_data=csv_data)):
        created, renamed, updated, deleted, warned = merge_communes(
            "merge.csv", False, io.StringIO()
        )
    assert created == 1
    assert models.Commune.objects.filter(insee="39378", postal="39190").exists()


@pytest.mark.django_db
def test_merge_pass1_warns_when_no_postal_and_no_old_commune():
    stdout = io.StringIO()
    # No old commune in DB and no postal in CSV
    csv_data = make_merge_csv(("39023", "39378", ""))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        created, renamed, updated, deleted, warned = merge_communes(
            "merge.csv", False, stdout
        )
    assert created == 0
    assert warned == 1
    assert "WARNING" in stdout.getvalue()


# --- Pass 2: update project references ---


@pytest.mark.django_db
def test_merge_pass2_updates_project_commune(dept_39):
    old_commune = baker.make(
        models.Commune, insee="39023", postal="39190", department=dept_39
    )
    new_commune = baker.make(
        models.Commune, insee="39378", postal="39320", department=dept_39
    )
    project = baker.make(project_models.Project, commune=old_commune)

    csv_data = make_merge_csv(("39023", "39378", "39320"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        created, renamed, updated, deleted, warned = merge_communes(
            "merge.csv", False, io.StringIO()
        )

    project.refresh_from_db()
    assert project.commune == new_commune
    assert updated == 1
    assert warned == 0


@pytest.mark.django_db
def test_merge_pass2_skips_when_no_projects(dept_39):
    baker.make(models.Commune, insee="39023", postal="39190", department=dept_39)
    baker.make(models.Commune, insee="39378", postal="39320", department=dept_39)

    csv_data = make_merge_csv(("39023", "39378", "39320"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        created, renamed, updated, deleted, warned = merge_communes(
            "merge.csv", False, io.StringIO()
        )
    assert updated == 0


# --- Pass 3: delete orphan old communes ---


@pytest.mark.django_db
def test_merge_pass3_deletes_orphan_old_commune(dept_39):
    baker.make(models.Commune, insee="39023", postal="39190", department=dept_39)
    baker.make(models.Commune, insee="39378", postal="39320", department=dept_39)

    csv_data = make_merge_csv(("39023", "39378", "39320"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        created, renamed, updated, deleted, warned = merge_communes(
            "merge.csv", False, io.StringIO()
        )
    assert deleted == 1
    assert not models.Commune.objects.filter(insee="39023").exists()


@pytest.mark.django_db
def test_merge_pass3_keeps_commune_still_used_by_project(dept_39):
    old_commune = baker.make(
        models.Commune, insee="39023", postal="39190", department=dept_39
    )
    baker.make(models.Commune, insee="39378", postal="39320", department=dept_39)
    baker.make(project_models.Project, commune=old_commune)

    csv_data = make_merge_csv(("39023", "39378", "39320"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        merge_communes("merge.csv", False, io.StringIO())

    # After pass 2 the project points to new commune; old commune is now orphan and deleted
    assert not models.Commune.objects.filter(insee="39023").exists()


@pytest.mark.django_db
def test_merge_pass3_does_not_delete_self_merging_commune(dept_39):
    baker.make(
        models.Commune,
        insee="39378",
        postal="39320",
        name="Commune Nouvelle",
        department=dept_39,
    )
    csv_data = make_merge_csv(("39378", "39378", "39320"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        created, renamed, updated, deleted, warned = merge_communes(
            "merge.csv", False, io.StringIO()
        )
    assert deleted == 0
    assert models.Commune.objects.filter(insee="39378").exists()


# --- Dry run ---


@pytest.mark.django_db
def test_merge_dry_run_does_not_write(dept_39):
    old_commune = baker.make(
        models.Commune, insee="39023", postal="39190", department=dept_39
    )
    baker.make(models.Commune, insee="39378", postal="39320", department=dept_39)
    project = baker.make(project_models.Project, commune=old_commune)

    csv_data = make_merge_csv(("39023", "39378", "39320"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        created, renamed, updated, deleted, warned = merge_communes(
            "merge.csv", True, io.StringIO()
        )

    project.refresh_from_db()
    assert project.commune == old_commune
    assert updated == 1
    assert deleted == 0
    assert models.Commune.objects.filter(insee="39023").exists()  # not deleted


# --- Management command ---


@pytest.mark.django_db
def test_mergecommunes_command_updates_project_and_prints_summary(capsys, dept_39):
    old_commune = baker.make(
        models.Commune, insee="39023", postal="39190", department=dept_39
    )
    new_commune = baker.make(
        models.Commune, insee="39378", postal="39320", department=dept_39
    )
    project = baker.make(project_models.Project, commune=old_commune)

    csv_data = make_merge_csv(("39023", "39378", "39320"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        call_command("mergecommunes", "merge.csv")

    project.refresh_from_db()
    assert project.commune == new_commune

    captured = capsys.readouterr()
    assert "Projects updated:  1" in captured.out
    assert "Communes deleted:  1" in captured.out
    assert "Warnings:          0" in captured.out


# eof
