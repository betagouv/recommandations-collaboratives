import pytest
from model_bakery import baker

from ..models import DSFolder, DSResource
from ..utils import MappingField


class TestDSResource:
    def test_property_number(self, ds_schema_sample):
        ds_resource = baker.prepare(DSResource)
        assert ds_resource.number is None

        ds_resource.schema = ds_schema_sample
        assert ds_resource.number == 80892

    def test_property_fields(self, ds_schema_sample):
        ds_resource = baker.prepare(DSResource)
        assert ds_resource.fields == [
            MappingField(id="identite_prenom", label="Prénom"),
            MappingField(id="identite_nom", label="Nom"),
        ]

        ds_resource.schema = ds_schema_sample
        assert len(ds_resource.fields) == 102

        assert ds_resource.fields[2] == MappingField(
            id="champ_Q2hhbXAtMjk5Njg5OA",
            label="Demandes de subventions DETR - DSIL 2024",
        )


class TestDSFolder:
    @pytest.mark.django_db
    def test_content_hash(self):
        ds_folder = baker.make(DSFolder, content={"foo": "bar"})
        assert (
            ds_folder.content_hash
            == "426fc04f04bf8fdb5831dc37bbb6dcf70f63a37e05a68c6ea5f63e85ae579376"
        )

    def test_prefilled_count(self):
        ds_folder = baker.prepare(DSFolder)
        assert ds_folder.prefilled_count == 0
        ds_folder.content = {"foo": "bar", "baz": "qux"}
        assert ds_folder.prefilled_count == 2
