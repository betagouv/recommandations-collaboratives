# encoding: utf-8

"""
Views for resources application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-06-16 10:59:08 CEST
"""

from django.contrib.auth.decorators import login_required

from django import forms

from django.utils import timezone

from django.urls import reverse

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from markdownx.fields import MarkdownxFormField

from urbanvitaliz.utils import is_staff_or_403

from urbanvitaliz.apps.projects import models as projects

from . import models


########################################################################
# Searching resources
########################################################################


def resource_search(request):
    """Search existing resources"""
    form = SearchForm(request.GET, initial={"limit_area": True})
    form.is_valid()
    query = form.cleaned_data.get("query", "")
    limit_area = form.cleaned_data.get("limit_area", True)
    categories = form.selected_categories

    # user communes from her projects if applicable
    communes = []
    if hasattr(request.user, "email"):
        communes = [p.commune for p in projects.Project.fetch(email=request.user.email)]
    if not communes:
        limit_area = None  # does not apply if no projects

    resources = models.Resource.search(query, categories)
    if not request.user.is_staff:
        resources = resources.filter(public=True)
    if limit_area:
        resources = resources.limit_area(communes)

    return render(request, "resources/resource/list.html", locals())


# NOTE both using search and filter in same action is slippy


class SearchForm(forms.Form):
    """Form to search for resources and filter by category"""

    query = forms.CharField(required=False)

    limit_area = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.the_categories = models.Category.fetch()
        # add one field per category defined in the database
        for category in self.the_categories:
            name = category.form_label
            field = forms.BooleanField(initial=True, required=False)
            self.fields[name] = field
            field.the_category = category

    @property
    def category_fields(self):
        """Return the fields for each category with their status"""
        categories = []
        for category in self.the_categories:
            # get the state of the category filter from the request
            checked = self.cleaned_data.get(category.form_label)
            categories.append(dict(the_category=category, checked=checked))
        return categories

    @property
    def selected_categories(self):
        """Return the list of selected categories to be filtered"""
        selected = []
        for category in self.the_categories:
            if self.cleaned_data.get(category.form_label):
                selected.append(category)
        return selected


########################################################################
# Seeing resources
########################################################################


@login_required
def resource_detail(request, resource_id=None):
    """Return the details of given resource"""
    resource = get_object_or_404(models.Resource, pk=resource_id)

    bookmark = models.Bookmark.objects.filter(
        resource=resource, created_by=request.user
    ).first()

    return render(request, "resources/resource/details.html", locals())


########################################################################
# Creating and updating resources
########################################################################


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Try to load the Markdown template into 'content' field
        try:
            tmpl = get_template(
                template_name="resources/resource/create_md_template.md"
            )
            self.fields["content"].initial = tmpl.render()
        except TemplateDoesNotExist:
            pass

    content = MarkdownxFormField(label="Contenu")

    title = forms.CharField(
        label="Titre", widget=forms.TextInput(attrs={"class": "form-control"})
    )
    subtitle = forms.CharField(
        label="Sous-Titre",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    summary = forms.CharField(
        label="Résumé bref",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    tags = forms.CharField(
        label="Mots-clés", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = models.Resource
        fields = [
            "title",
            "subtitle",
            "summary",
            "tags",
            "category",
            "departments",
            "content",
        ]


########################################################################
# bookmark resources
########################################################################


@login_required
def create_bookmark(request, resource_id=None):
    """Create bookmark for resource and and connected user"""
    resource = get_object_or_404(models.Resource, pk=resource_id)
    try:
        # look if bookmark exists and is deleted
        bookmark = models.Bookmark.deleted_objects.get(
            resource=resource, created_by=request.user
        )
    except models.Bookmark.DoesNotExist:
        bookmark, _ = models.Bookmark.objects.get_or_create(
            resource=resource, created_by=request.user
        )
    if request.method == "POST":
        form = BookmarkForm(request.POST, instance=bookmark)
        if form.is_valid():
            # save bookmark with comments
            instance = form.save(commit=False)
            instance.deleted = None
            instance.save()
            next_url = reverse("resources-resource-detail", args=[resource.id])
            return redirect(next_url)
    else:
        form = BookmarkForm(instance=bookmark)
    return render(request, "resources/bookmark/create.html", locals())


class BookmarkForm(forms.ModelForm):
    """Create and update bookmark"""

    class Meta:
        model = models.Bookmark
        fields = ["comments"]


@login_required
def delete_bookmark(request, resource_id=None):
    """Delete (soft) user bookmark associated to resource if exists"""
    if request.method == "POST":
        try:
            bookmark = models.Bookmark.objects.get(
                resource_id=resource_id, created_by=request.user
            )
            bookmark.deleted = timezone.now()
            bookmark.save()
        except models.Bookmark.DoesNotExist:
            pass
    next_url = reverse("resources-resource-detail", args=[resource_id])
    return redirect(next_url)


# eof
