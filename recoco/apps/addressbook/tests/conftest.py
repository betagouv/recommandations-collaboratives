import pytest
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from model_bakery import baker


@pytest.fixture
def current_site():
    return Site.objects.filter(domain="example.com").first()


@pytest.fixture
def staff_user():
    site = Site.objects.filter(domain="example.com").first()
    staff = baker.make(User)
    staff.profile.sites.add(site)
    gstaff = Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)
    return staff
