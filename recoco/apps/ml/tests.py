import pytest
from django.shortcuts import reverse
from model_bakery import baker
from pytest_django.asserts import assertRedirects

from recoco.apps.resources import models as resources_models
from recoco.utils import login

from . import models


@pytest.mark.django_db
def test_propose_resource_comparison_redirects_to_comparison_page(
    request, client, current_site
):
    resource = baker.make(
        resources_models.Resource,
        sites=[current_site],
        status=resources_models.Resource.PUBLISHED,
    )
    baker.make(models.Summary, content_object=resource, text="Aloa1")
    baker.make(models.Summary, content_object=resource, text="Aloa2")
    url = reverse("ml-resource-comparison-propose")

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    comparison = models.Comparison.objects.first()
    assertRedirects(
        response, reverse("ml-resource-comparison-show", args=(comparison.id,))
    )


@pytest.mark.django_db
def test_propose_resource_comparison_when_nothing_to_do(request, client, current_site):
    resource = baker.make(
        resources_models.Resource,
        sites=[current_site],
        status=resources_models.Resource.PUBLISHED,
    )
    baker.make(models.Summary, content_object=resource, text="Aloa")

    url = reverse("ml-resource-comparison-propose")

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_propose_return_pending_comparison(request, client, current_site):
    resource = baker.make(
        resources_models.Resource,
        sites=[current_site],
        status=resources_models.Resource.PUBLISHED,
    )

    url = reverse("ml-resource-comparison-propose")

    with login(client, groups=["example_com_staff"]) as user:
        comparison = baker.make(
            models.Comparison,
            user=user,
            summary1__content_object=resource,
            summary2__content_object=resource,
            choice=None,
        )
        response = client.get(url)

    expected = reverse("ml-resource-comparison-show", args=[comparison.id])
    assertRedirects(response, expected)


@pytest.mark.django_db
def test_comparison_update(request, client, current_site):
    resource = baker.make(
        resources_models.Resource,
        sites=[current_site],
        status=resources_models.Resource.PUBLISHED,
    )

    with login(client, groups=["example_com_staff"]) as user:
        comparison = baker.make(
            models.Comparison,
            user=user,
            summary1__content_object=resource,
            summary2__content_object=resource,
            choice=None,
        )
        url = reverse("ml-comparison-update", args=[comparison.id])
        response = client.post(url, data={"choice": 1})

    comparison.refresh_from_db()

    assert comparison.choice == 1

    assertRedirects(response, reverse("ml-resource-comparison-propose"))
