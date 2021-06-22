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
    """Search existing resources"""
    form = SearchForm(request.GET)
    form.is_valid()
    query = form.cleaned_data.get("query", "")
    categories = form.selected_categories
    resources = models.Resource.search(query, categories)
    return render(request, "resources/resource/list.html", locals())


class SearchForm(forms.Form):
    """Form to search for resources"""

    query = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.the_categories = models.Category.fetch()
        self.categories = []
        for category in self.the_categories:
            name = category.form_label
            attr = forms.BooleanField(initial=True)
            setattr(self, name, attr)
            attr.input_name = name
            self.categories.append(category)

    @property
    def selected_categories(self):
        selected = []
        for category in self.the_categories:
            name = f"cat{category.id}"
            if hasattr(self, name) and getattr(self, name):
                selected.append(category)
        return selected


@login_required
def resource_detail(request, resource_id=None):
    """Return the details of given resource"""
    resource = get_object_or_404(models.Resource, pk=resource_id)
    return render(request, "resources/resource/details.html", locals())


@login_required
def resource_update(request, resource_id=None):
    """Update informations for resource"""
    is_staff_or_403(request.user)
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
    is_staff_or_403(request.user)
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


########################################################################
# Helpers
########################################################################


def is_staff_or_403(user):
    """Raise a 403 error is user is not a staff member"""
    if not user or not user.is_staff:
        raise PermissionDenied("L'information demandée n'est pas disponible")


# eof
