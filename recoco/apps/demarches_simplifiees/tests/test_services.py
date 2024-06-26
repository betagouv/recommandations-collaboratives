import pytest
from model_bakery import baker

from recoco.apps.projects.models import Project

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
            find_ds_resource_for_project(baker.prepare(Project, commune=None)) is None
        )

    @pytest.mark.django_db
    def test_filter_dept(self):
        ds_resource = baker.make(DSResource, type="DETR_DSIL", departments__code="64")
        assert (
            find_ds_resource_for_project(
                baker.make(Project, commune__department__code="01")
            )
            is None
        )
        assert (
            find_ds_resource_for_project(
                baker.make(Project, commune__department__code="64")
            )
            == ds_resource
        )
