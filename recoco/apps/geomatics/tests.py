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

MERGE_CSV_HEADER = "Date,Code INSEE Commune Nouvelle,Nom Commune Nouvelle Siège,Code INSEE Commune Déléguée (non actif),Nom Commune Déléguée\n"


def make_merge_csv(*rows):
    """Build a merge CSV string from (old_insee, new_insee) pairs."""
    lines = MERGE_CSV_HEADER
    for old, new in rows:
        lines += f"AVRIL 2016,{new},Commune Nouvelle,{old},Commune Déléguée\n"
    return lines


@pytest.mark.django_db
def test_merge_communes_not_applicable_when_no_project_uses_old_insee():
    csv_data = make_merge_csv(("39023", "39378"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        updated, warned, not_applicable = merge_communes(
            "merge.csv", False, io.StringIO(), io.StringIO()
        )
    assert updated == 0
    assert warned == 0
    assert not_applicable == 1


@pytest.mark.django_db
def test_merge_communes_updates_project_commune():
    old_commune = baker.make(models.Commune, insee="39023", postal="39190")
    new_commune = baker.make(models.Commune, insee="39378", postal="39320")
    project = baker.make(project_models.Project, commune=old_commune)

    csv_data = make_merge_csv(("39023", "39378"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        updated, warned, not_applicable = merge_communes(
            "merge.csv", False, io.StringIO(), io.StringIO()
        )

    project.refresh_from_db()
    assert project.commune == new_commune
    assert updated == 1
    assert warned == 0
    assert not_applicable == 0


@pytest.mark.django_db
def test_merge_communes_warns_when_new_commune_not_in_db():
    old_commune = baker.make(models.Commune, insee="39023", postal="39190")
    baker.make(project_models.Project, commune=old_commune)

    stdout = io.StringIO()
    csv_data = make_merge_csv(("39023", "39378"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        updated, warned, not_applicable = merge_communes(
            "merge.csv", False, stdout, io.StringIO()
        )

    assert updated == 0
    assert warned == 1
    assert not_applicable == 0
    assert "WARNING" in stdout.getvalue()
    assert "39378" in stdout.getvalue()


@pytest.mark.django_db
def test_merge_communes_dry_run_does_not_update():
    old_commune = baker.make(models.Commune, insee="39023", postal="39190")
    baker.make(models.Commune, insee="39378", postal="39320")
    project = baker.make(project_models.Project, commune=old_commune)

    csv_data = make_merge_csv(("39023", "39378"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        updated, warned, not_applicable = merge_communes(
            "merge.csv", True, io.StringIO(), io.StringIO()
        )

    project.refresh_from_db()
    assert project.commune == old_commune
    assert updated == 1  # counts would-be updates
    assert warned == 0
    assert not_applicable == 0


@pytest.mark.django_db
def test_mergecommunes_command_updates_project_commune(capsys):
    old_commune = baker.make(models.Commune, insee="39023", postal="39190")
    new_commune = baker.make(models.Commune, insee="39378", postal="39320")
    project = baker.make(project_models.Project, commune=old_commune)

    csv_data = make_merge_csv(("39023", "39378"))
    with patch("builtins.open", mock_open(read_data=csv_data)):
        call_command("mergecommunes", "merge.csv")

    project.refresh_from_db()
    assert project.commune == new_commune

    captured = capsys.readouterr()
    assert "Projects updated:              1" in captured.out
    assert "Warnings (new commune missing): 0" in captured.out
    assert "Not applicable (no projects):   0" in captured.out


# eof
