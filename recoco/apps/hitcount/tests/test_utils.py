import pytest
from django.contrib.contenttypes.models import ContentType

from recoco.apps.addressbook.models import Contact
from recoco.apps.hitcount.utils import ct_from_label


@pytest.mark.django_db
def test_ct_from_label():
    contact_ct = ContentType.objects.get_for_model(Contact)
    assert ct_from_label("addressbook.contact") == contact_ct
    assert ct_from_label("addressbook.dummy") is None
    assert ct_from_label("dummy-value") is None
    assert ct_from_label("addressbook.") is None
