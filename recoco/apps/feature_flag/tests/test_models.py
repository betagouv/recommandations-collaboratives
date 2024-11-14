import pytest
from django.contrib.sites.models import Site
from django.test.client import RequestFactory
from waffle import flag_is_active, sample_is_active, switch_is_active

from recoco.apps.feature_flag.models import Flag, Sample, Switch


@pytest.mark.django_db
class TestCustomModels:
    def setup_method(self):
        self.site_one = Site.objects.first()
        assert self.site_one is not None
        self.site_two = Site.objects.create(domain="acme.com", name="acme")
        current_site = Site.objects.get_current()
        assert current_site == self.site_one

    def test_switch(self):
        switch = Switch.objects.create(name="test_switch", active=True)
        assert switch_is_active("test_switch") is True

        switch.sites.add(self.site_two)
        assert switch_is_active("test_switch") is False

        switch.sites.add(self.site_one)
        assert switch_is_active("test_switch") is True

    def test_flag(self):
        request = RequestFactory().get("/")

        flag = Flag.objects.create(name="test_flag", everyone=True)
        assert flag_is_active(request, "test_flag") is True

        flag.sites.add(self.site_two)
        assert flag_is_active(request, "test_flag") is False

        flag.sites.add(self.site_one)
        assert flag_is_active(request, "test_flag") is True

    def test_sample(self):
        sample = Sample.objects.create(name="test_sample", percent=100.0)
        assert sample_is_active("test_sample") is True

        sample.sites.add(self.site_two)
        assert sample_is_active("test_sample") is False

        sample.sites.add(self.site_one)
        assert sample_is_active("test_sample") is True
