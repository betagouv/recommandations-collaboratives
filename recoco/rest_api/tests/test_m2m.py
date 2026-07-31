import pytest

from ..m2m.urls import urlpatterns
from ..permissions import IsM2MPartner


@pytest.mark.parametrize(
    "pattern", urlpatterns, ids=lambda pattern: str(pattern.pattern)
)
def test_m2m_endpoint_is_restricted_to_m2m_partners(pattern):
    """No path of the m2m namespace is open to anyone else, schema included"""
    view = pattern.callback

    assert view.initkwargs.get("permission_classes", view.cls.permission_classes) == [
        IsM2MPartner
    ]
