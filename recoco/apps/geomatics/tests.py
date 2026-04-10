# encoding: utf-8

"""
Testing geomatics application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-10-11 19:06:54 CEST
"""

from unittest.mock import mock_open, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from . import models


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
def test_load_file_reports_stats(capsys):
    with patch("builtins.open", mock_open(read_data=CSV)):
        call_command("loadcommunes", "communes.csv")
    captured = capsys.readouterr()
    assert "Newly created:    1" in captured.out
    assert "Already existing: 0" in captured.out
    assert "Only in DB:       0" in captured.out


@pytest.mark.django_db
def test_load_file_existing_commune_not_duplicated():
    with patch("builtins.open", mock_open(read_data=CSV)):
        call_command("loadcommunes", "communes.csv")
        call_command("loadcommunes", "communes.csv")
    assert models.Commune.objects.count() == 1


CSV = """,code_insee,nom_standard,code_postal,dep_code,dep_nom,reg_code,reg_nom,latitude_centre,longitude_centre
0,01001,L'Abergement-Clémenciat,01400,01,Ain,84,Auvergne-Rhône-Alpes,46.153,4.926
"""

# eof
