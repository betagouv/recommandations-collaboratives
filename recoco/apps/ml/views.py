import random
from itertools import combinations

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render

from recoco.apps.resources import models as resources_models

from .models import Comparison, Summary


def compare_resource(request, resource_id):
    resource = get_object_or_404(resources_models.Resource, pk=resource_id)
    resource_ct = ContentType.objects.get_for_model(resource)

    available_summaries = (
        Summary.objects.filter(object_id=resource.pk, content_type=resource_ct)
        .exclude(text="")
        .values_list("id", flat=True)
    )
    candidates = set(combinations(available_summaries, 2))

    existings = set(
        Comparison.objects.filter(
            user=request.user,
            summary1__content_type=resource_ct,
            summary1__object_id=resource.id,
        ).values_list("summary1__pk", "summary2__pk")
    )

    (sum1, sum2) = random.choice(tuple(candidates - existings))  # noqa: S311

    comparison = Comparison.objects.create(
        user=request.user, summary1_id=sum1, summary2_id=sum2
    )

    return render(request, "ml/compare_resource.html", locals())
