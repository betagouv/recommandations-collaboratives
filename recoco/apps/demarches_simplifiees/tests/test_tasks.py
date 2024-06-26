from unittest.mock import patch

import pytest
import responses
from django.conf import settings
from model_bakery import baker

from recoco.apps.tasks.models import Task

from ..exceptions import DSAPIError
from ..models import DSFolder, DSResource
from ..tasks import load_ds_resource_schema, update_or_create_ds_folder
from .base import BaseTestMixin


@pytest.mark.django_db
class TestLoadDSResourceSchema(BaseTestMixin):
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


@pytest.mark.django_db
class TestUpdateOrCreateDSFolder(BaseTestMixin):
    ds_url = f"{settings.DS_API_BASE_URL}/demarches/80892/dossiers"

    @responses.activate
    def test_no_ds_resource(self):
        responses.post(url=self.ds_url)
        update_or_create_ds_folder(9999)
        responses.assert_call_count(self.ds_url, 0)
        assert DSFolder.objects.count() == 0

    @responses.activate
    def test_no_ds_resource_match(self):
        recommendation = baker.make(Task)

        responses.post(url=self.ds_url)

        with patch(
            "recoco.apps.demarches_simplifiees.tasks.find_ds_resource_for_project",
            return_value=None,
        ):
            update_or_create_ds_folder(recommendation.id)

        responses.assert_call_count(self.ds_url, 0)
        assert DSFolder.objects.count() == 0

    @responses.activate
    def test_no_ds_resource_number(self):
        recommendation = baker.make(Task)
        ds_resource = baker.make(DSResource, schema={"foo": "bar"})
        assert ds_resource.number is None

        responses.post(url=self.ds_url)

        with patch(
            "recoco.apps.demarches_simplifiees.tasks.find_ds_resource_for_project",
            return_value=ds_resource,
        ) as mock_find_ds_resource_for_project:
            update_or_create_ds_folder(recommendation.id)

        mock_find_ds_resource_for_project.assert_called_once_with(
            project=recommendation.project
        )
        responses.assert_call_count(self.ds_url, 0)
        assert DSFolder.objects.count() == 0

    @responses.activate
    def test_bad_response(self, ds_schema_sample):
        recommendation = baker.make(Task, project__name="my-project")
        ds_resource = baker.make(DSResource, schema=ds_schema_sample)

        responses.post(url=self.ds_url, status=400)

        with patch(
            "recoco.apps.demarches_simplifiees.tasks.find_ds_resource_for_project",
            return_value=ds_resource,
        ) as mock_find_ds_resource_for_project:
            with pytest.raises(DSAPIError):
                update_or_create_ds_folder(recommendation.id)

        mock_find_ds_resource_for_project.assert_called_once_with(
            project=recommendation.project
        )
        responses.assert_call_count(self.ds_url, 1)
        assert DSFolder.objects.count() == 0

    @responses.activate
    def test_ds_folder_created(self, ds_schema_sample):
        recommendation = baker.make(Task, project__name="my-project")
        ds_resource = baker.make(DSResource, schema=ds_schema_sample)

        responses.post(
            url=self.ds_url,
            status=201,
            json={
                "dossier_id": "12345",
                "dossier_url": "https://example.com/dossiers/12345",
                "dossier_number": 12345,
                "dossier_prefill_token": "prefill-token",  # nosec
                "state": "prefilled",
            },
        )

        with patch(
            "recoco.apps.demarches_simplifiees.tasks.find_ds_resource_for_project",
            return_value=ds_resource,
        ) as mock_find_ds_resource_for_project:
            update_or_create_ds_folder(recommendation.id)

        mock_find_ds_resource_for_project.assert_called_once_with(
            project=recommendation.project
        )
        responses.assert_call_count(self.ds_url, 1)

        ds_folder = DSFolder.objects.first()
        assert ds_folder is not None
        assert ds_folder.project == recommendation.project
        assert ds_folder.ds_resource == ds_resource
        assert ds_folder.dossier_id == "12345"
        assert ds_folder.dossier_url == "https://example.com/dossiers/12345"
        assert ds_folder.dossier_number == 12345
        assert ds_folder.dossier_prefill_token == "prefill-token"  # nosec
        assert ds_folder.state == "prefilled"
        assert ds_folder.content == {"champ_Q2hhbXAtMjk3MTQ0NA": "my-project"}
        assert (
            ds_folder.content_hash
            == "9cd55d887a3e036cd6107553d52f804415b6b3d74ecb65b268188c1596eab748"
        )
        assert ds_folder.recommendation == recommendation

    @responses.activate
    def test_ds_folder_already_exist(self, ds_schema_sample):
        recommendation = baker.make(Task, project__name="my-project")
        ds_resource = baker.make(DSResource, schema=ds_schema_sample)

        ds_folder = baker.make(
            DSFolder,
            project=recommendation.project,
            ds_resource=ds_resource,
            content={"champ_Q2hhbXAtMjk3MTQ0NA": "my-project"},
        )
        assert (
            ds_folder.content_hash
            == "9cd55d887a3e036cd6107553d52f804415b6b3d74ecb65b268188c1596eab748"
        )

        responses.post(url=self.ds_url, status=201)

        with patch(
            "recoco.apps.demarches_simplifiees.tasks.find_ds_resource_for_project",
            return_value=ds_resource,
        ):
            update_or_create_ds_folder(recommendation.id)

        responses.assert_call_count(self.ds_url, 0)
