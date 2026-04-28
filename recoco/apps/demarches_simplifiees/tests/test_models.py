from model_bakery import baker

from ..models import DSResource
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
