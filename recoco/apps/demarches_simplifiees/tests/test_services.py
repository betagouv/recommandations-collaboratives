import pytest
from model_bakery import baker

from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource

from ..models import DSMappingField, DSResource
from ..services import (
    find_ds_resource_for_project,
    make_ds_data_from_project,
)
from .base import BaseTestMixin


class TestMakeDSDataFromProject(BaseTestMixin):
    @pytest.mark.django_db
    def test_no_mapping_fields(self):
        project = baker.make(Project, name="my project")
        ds_resource = baker.make(DSResource)
        assert (
            make_ds_data_from_project(
                project=project,
                ds_resource=ds_resource,
            )
            == {}
        )

    @pytest.mark.django_db
    def test_mapping_done(self):
        project = baker.make(Project, name="my project")
        ds_resource = baker.make(DSResource)
        baker.make(
            DSMappingField,
            ds_resource=ds_resource,
            field_id="123",
            project_lookup_key="name",
        )

        assert make_ds_data_from_project(
            project=project,
            ds_resource=ds_resource,
        ) == {"123": "my project"}


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
