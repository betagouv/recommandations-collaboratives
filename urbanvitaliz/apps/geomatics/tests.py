# encoding: utf-8

"""
Testing geomatics application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-10-11 19:06:54 CEST
"""

from unittest.mock import patch, mock_open

import pytest

from django.core.management.base import CommandError
from django.core.management import call_command

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
        call_command("loadcommunes", "empty.csv")
    region = models.Region.objects.all()[0]
    assert region.name == "Auvergne-Rhône-Alpes"
    assert region.code == "84"
    department = models.Department.objects.all()[0]
    assert department.name == "Ain"
    assert department.code == "1"
    commune = models.Commune.objects.all()[0]
    assert commune.name == "L ABERGEMENT CLEMENCIAT"
    assert commune.insee == "1001"
    assert commune.postal == "1400"


CSV = """code_commune_INSEE,nom_commune_postal,code_postal,libelle_acheminement,ligne_5,latitude,longitude,code_commune,article,nom_commune,nom_commune_complet,code_departement,nom_departement,code_region,nom_region
1001,L ABERGEMENT CLEMENCIAT,1400,L ABERGEMENT CLEMENCIAT,,46.1534255214,4.92611354223,1,L',Abergement-Clémenciat,L'Abergement-Clémenciat,1,Ain,84,Auvergne-Rhône-Alpes
"""

# eof
