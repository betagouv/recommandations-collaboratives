import pytest
from django.shortcuts import reverse
from model_bakery import baker

from recoco.apps.resources import models as resources_models
from recoco.utils import login

from . import models


@pytest.mark.django_db
def test_compare_available_for_staff(request, client, current_site):
    resource = baker.make(resources_models.Resource)
    baker.make(models.Summary, content_object=resource, text="Aloa1")
    baker.make(models.Summary, content_object=resource, text="Aloa2")
    url = reverse("ml-compare-resource", args=[resource.pk])

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_compare_when_no_options(request, client, current_site):
    resource = baker.make(resources_models.Resource)
    baker.make(models.Summary, content_object=resource, text="Aloa")

    url = reverse("ml-compare-resource", args=[resource.pk])

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_compare_reuses_comparison_if_no_choice_picked(request, client, current_site):
    resource = baker.make(resources_models.Resource)

    url = reverse("ml-compare-resource", args=[resource.pk])

    with login(client, groups=["example_com_staff"]) as user:
        baker.make(
            models.Comparison,
            user=user,
            summary1__content_object=resource,
            summary2__content_object=resource,
            choice=None,
        )
        response = client.get(url)

    assert response.status_code == 200

    assert models.Comparison.objects.count() == 1
