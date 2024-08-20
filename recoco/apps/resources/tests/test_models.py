import pytest
from model_bakery import baker


@pytest.mark.django_db
def test_is_dsresource():
    resource = baker.make("resources.Resource")
    assert resource.is_dsresource is False
    baker.make("demarches_simplifiees.DSResource", resource=resource)
    assert resource.is_dsresource is True
