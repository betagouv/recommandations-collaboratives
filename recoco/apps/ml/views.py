import random
from itertools import combinations

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render, reverse

from recoco.apps.resources import models as resources_models

from . import forms
from .models import Comparison, Summary


def propose_resource_comparison(request):
    # une proposition non répondueow -> on prend la première
    pending = Comparison.objects.filter(user=request.user, choice=None).first()
    if pending:
        url = reverse("ml-resource-comparison-show", args=(pending.id,))
        return redirect(url)

    # trouver une resource pour cet utilisateur

    resources = resources_models.Resource.objects.filter(
        sites=request.site, status=resources_models.Resource.PUBLISHED
    ).order_by("?")

    resource_ct = ContentType.objects.get_for_model(resources_models.Resource)

    for resource in resources:
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
            )
            .exclude(choice=None)
            .values_list("summary1__pk", "summary2__pk")
        )

        options = tuple(candidates - existings)

        if options:
            sum1, sum2 = random.choice(options)  # noqa: S311

            comparison, _ = Comparison.objects.get_or_create(
                user=request.user, summary1_id=sum1, summary2_id=sum2, choice=None
            )
            return redirect(
                reverse("ml-resource-comparison-show", args=(comparison.id,))
            )

    # no solution found
    return render(request, "ml/no_comparison.html")


def show_resource_comparison(request, comparison_id):
    comparison = get_object_or_404(Comparison, pk=comparison_id)

    # TODO check that this comparison is about resources

    form = forms.ComparisonForm(instance=comparison)

    return render(request, "ml/compare_resource.html", locals())


def update_comparison(request, comparison_id):
    comparison = get_object_or_404(Comparison, pk=comparison_id)
    if request.method == "POST":
        form = forms.ComparisonForm(request.POST, instance=comparison)
        if form.is_valid():
            form.save()
    return redirect(reverse("ml-resource-comparison-propose"))
