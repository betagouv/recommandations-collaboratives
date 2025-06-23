import pytest

from recoco.apps.addressbook.models import Organization, OrganizationGroup


@pytest.mark.django_db
def test_create_organisation_national_group():
    assert not Organization.objects.filter(name="Jedi Order").exists()
    assert not OrganizationGroup.objects.filter(name="Jedi Order").exists()

    org = Organization(name="Jedi Order")
    org.save()

    org.refresh_from_db()
    group = OrganizationGroup.objects.filter(name="Jedi Order").first()
    assert group is not None
    assert org.group == group
