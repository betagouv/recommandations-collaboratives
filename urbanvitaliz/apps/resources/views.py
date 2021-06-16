# encoding: utf-8

"""
Views for resources application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-06-16 10:59:08 CEST
"""

from django.contrib.auth.decorators import login_required

from django.core.exceptions import PermissionDenied

from django import forms

from django.urls import reverse

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from markdownx.fields import MarkdownxFormField

from . import models


@login_required
def resource_search(request):
    """Search exisiting resources"""
    if request.method == "POST":
        request.session["resources_resource_search_criterias"] = request.POST.get(
            "criterias", ""
        )
    criterias = request.session.get("resources_resource_search_criterias", "")
    resources = models.Resource.search(criterias)
    return render(request, "resources/resource/list.html", locals())


@login_required
def resource_detail(request, resource_id=None):
    """Return the details of given resource"""
    resource = get_object_or_404(models.Resource, pk=resource_id)
    return render(request, "resources/resource/details.html", locals())


@login_required
def resource_update(request, resource_id=None):
    """Update informations for resource"""
    resource = get_object_or_404(models.Resource, pk=resource_id)
    next_url = reverse("resources-resource-detail", args=[resource.id])
    if request.method == "POST":
        form = EditResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            return redirect(next_url)
    else:
        form = EditResourceForm(instance=resource)
    return render(request, "resources/resource/update.html", locals())


@login_required
def resource_create(request):
    """Create new resource"""
    if request.method == "POST":
        form = EditResourceForm(request.POST)
        if form.is_valid():
            resource = form.save()
            next_url = reverse("resources-resource-detail", args=[resource.id])
            return redirect(next_url)
    else:
        form = EditResourceForm()
    return render(request, "resources/resource/create.html", locals())


class EditResourceForm(forms.ModelForm):
    """Create and update form for resources"""

    content = MarkdownxFormField()

    class Meta:
        model = models.Resource
        fields = ["title", "content"]


# eof
