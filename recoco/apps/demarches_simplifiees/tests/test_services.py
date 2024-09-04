import pytest
from model_bakery import baker

from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource

from ..models import DSResource
from ..services import (
    find_ds_resource_for_project,
    make_ds_data_from_project,
)
from .base import BaseTestMixin


class TestMakeDSDataFromProject(BaseTestMixin):
    def test_no_adapter_module(self):
        assert (
            make_ds_data_from_project(
                project=baker.prepare(Project),
                ds_resource=baker.prepare(DSResource, schema={"number": 123}),
            )
            == {}
        )

    def test_adapter_module(self, ds_schema_sample):
        assert make_ds_data_from_project(
            project=baker.prepare(Project, name="Mon projet"),
            ds_resource=baker.prepare(DSResource, schema=ds_schema_sample),
        ) == {
            "champ_Q2hhbXAtMjk3MTQ0NA": "Mon projet",
        }


class TestfindDSResourceForProject(BaseTestMixin):
    def test_no_commune(self):
        assert (
            find_ds_resource_for_project(
                project=baker.prepare(Project, commune=None),
                resource=baker.prepare(Resource),
            )
            is None
        )

    @pytest.mark.django_db
    def test_filter_dept(self):
        resource = baker.make(Resource)
        ds_resource = baker.make(
            DSResource,
            resource=resource,
            departments__code="64",
        )
        assert (
            find_ds_resource_for_project(
                project=baker.make(Project, commune__department__code="01"),
                resource=resource,
            )
            is None
        )
        assert (
            find_ds_resource_for_project(
                project=baker.make(Project, commune__department__code="64"),
                resource=resource,
            )
            == ds_resource
        )
