import pytest

from ..m2m.urls import api_urls
from ..permissions import IsM2MPartner


@pytest.mark.parametrize("pattern", api_urls, ids=lambda pattern: str(pattern.pattern))
def test_m2m_endpoint_is_restricted_to_m2m_partners(pattern):
    """No endpoint of the m2m namespace is open to anyone else"""
    assert pattern.callback.cls.permission_classes == [IsM2MPartner]
