import pytest
from django.urls import reverse
# from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker
from pytest_django.asserts import assertContains
# from urbanvitaliz.apps.home import models as home_models
# from urbanvitaliz.apps.dsrc import models as dsrc_models
########################################################################
# Baker addons for using dynamic forms
########################################################################


def gen_dsrc_field_func():
    return """[{ "type": "text",
    "required": false,
    "label": "Text Field",
    "className": "form-control",
    "name": "text-1657009260220-0",
    "subtype": "text" }]"""


baker.generators.add("dynamic_forms.models.FormField", gen_dsrc_field_func)


@pytest.mark.django_db
def test_dsrc_page_is_reachable(request, client):
    # dsrc_config = dsrc_models.DsrcConfig.objects.first()

    # baker.make(
    #     home_models.SiteConfiguration,
    #     site=get_current_site(request),
    #     dsrc=dsrc_config,
    # )

    url = reverse("dsrc")
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-onboarding"')