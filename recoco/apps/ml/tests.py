import pytest
from django.shortcuts import reverse
from model_bakery import baker

from recoco.apps.resources import models as resources_models
from recoco.utils import login


@pytest.mark.django_db
def test_comapre_available_for_staff(request, client, current_site):
    resource = baker.make(resources_models.Resource)
    url = reverse("ml-compare-resource", args=[resource.pk])

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200
