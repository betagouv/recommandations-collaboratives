import pytest
from model_bakery import baker

from recoco.apps.resources.models import Resource


@pytest.mark.django_db
def test_with_ds_annotations():
    baker.make("resources.Resource")
    assert Resource.objects.count() == 1

    resource = Resource.objects.with_ds_annotations().first()
    assert resource.count_dsresource == 0
    assert resource.has_dsresource is False

    baker.make("demarches_simplifiees.DSResource", resource=resource)

    resource = Resource.objects.with_ds_annotations().first()
    assert resource.count_dsresource == 1
    assert resource.has_dsresource is True
