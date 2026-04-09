import pytest
import responses
from django.conf import settings
from model_bakery import baker

from ..exceptions import DSAPIError
from ..models import DSResource
from ..services import load_ds_resource_schema


@pytest.mark.django_db
class TestLoadDSResourceSchema:
    ds_url = f"{settings.DS_BASE_URL}/preremplir/ds-name/schema"

    @responses.activate
    def test_no_ds_resource(self):
        responses.get(url=self.ds_url)
        load_ds_resource_schema(9999)
        responses.assert_call_count(self.ds_url, 0)

    @responses.activate
    def test_schema_already_set(self):
        ds_resource = baker.make(DSResource, name="ds-name", schema={"foo": "bar"})
        responses.get(url=self.ds_url)
        load_ds_resource_schema(ds_resource.id)
        responses.assert_call_count(self.ds_url, 0)

    @responses.activate
    def test_bad_response(self):
        ds_resource = baker.make(DSResource, name="ds-name", schema=None)
        responses.get(url=self.ds_url, status=500)
        with pytest.raises(DSAPIError):
            load_ds_resource_schema(ds_resource.id)
        responses.assert_call_count(self.ds_url, 1)

    @responses.activate
    def test_schema_loaded(self, ds_schema_sample):
        ds_resource = baker.make(DSResource, name="ds-name", schema={})
        responses.get(url=self.ds_url, json=ds_schema_sample)
        load_ds_resource_schema(ds_resource.id)
        responses.assert_call_count(self.ds_url, 1)
        ds_resource.refresh_from_db()
        assert ds_resource.schema == ds_schema_sample
