import pytest
from model_bakery import baker

from recoco.apps.demarches_simplifiees.models import DSFolder, DSResource


class TestDSResource:
    def test_property_number(self, ds_schema_sample):
        ds_resource = baker.prepare(DSResource)
        assert ds_resource.number is None

        ds_resource.schema = ds_schema_sample
        assert ds_resource.number == 80892


class TestDSFolder:
    @pytest.mark.django_db
    def test_content_hash(self):
        ds_folder = baker.make(DSFolder, content={"foo": "bar"})
        assert (
            ds_folder.content_hash
            == "426fc04f04bf8fdb5831dc37bbb6dcf70f63a37e05a68c6ea5f63e85ae579376"
        )
