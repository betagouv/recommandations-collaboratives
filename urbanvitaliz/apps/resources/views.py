# encoding: utf-8

"""
Views for resources application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-06-16 10:59:08 CEST
"""
import datetime

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import Feed
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.views.generic.detail import DetailView
from markdownx.fields import MarkdownxFormField
from rest_framework import permissions, viewsets
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics_models
from urbanvitaliz.apps.projects import models as projects
from urbanvitaliz.utils import (
    check_if_switchtender,
    is_staff_or_403,
    is_switchtender_or_403,
)

from . import models
from .serializers import ResourceSerializer

########################################################################
# Searching resources
########################################################################


def resource_search(request):
    """Search existing resources"""
    form = SearchForm(request.GET)
    form.is_valid()
    query = form.cleaned_data.get("query", "")

    limit_area = form.cleaned_data.get("limit_area")
    searching = form.cleaned_data.get("searching", False)

    if (not searching) and (limit_area is None):
        limit_area = "AUTO"

    categories = form.selected_categories

    resources = models.Resource.search(query, categories)
    if not request.user.is_staff:
        # If we are staff, show also PRIVATE resources
        resources = resources.filter(status__gte=models.Resource.TO_REVIEW)

    # If we are a switchtender, allow any departement to be filtered
    # Otherwise, show only departments related to my projects
    departments = geomatics_models.Department.objects.none()
    if check_if_switchtender(request.user):
        departments = geomatics_models.Department.objects.order_by("name").all()
        if limit_area:
            selected_departments = geomatics_models.Department.objects.none()
            if limit_area == "AUTO":
                # Select departments from profile
                user_departments = request.user.profile.departments.all()
                if user_departments:
                    selected_departments = geomatics_models.Department.objects.filter(
                        code__in=user_departments
                    )
                else:
                    limit_area = None
            else:
                # Get current one from parameters
                selected_departments = geomatics_models.Department.objects.filter(
                    code=limit_area
                )

            if selected_departments:
                resources = resources.limit_area(selected_departments)

    else:
        communes = []
        if hasattr(request.user, "email"):
            communes = [
                p.commune for p in projects.Project.fetch(email=request.user.email)
            ]
            if not communes:
                limit_area = None  # does not apply if no projects

            departments = set(c.department for c in communes if c)
            if limit_area:
                resources = resources.limit_area(departments)

    # filter out expired
    expired = form.cleaned_data.get("expired", False)
    if expired:
        resources = resources.filter(Q(expires_on__lte=datetime.date.today()))

    # filter out 'to be reviewed'
    to_review = form.cleaned_data.get("to_review", False)
    if to_review:
        resources = resources.filter(status=models.Resource.TO_REVIEW)

    return render(request, "resources/resource/list.html", locals())


# NOTE both using search and filter in same action is slippy


class SearchForm(forms.Form):
    """Form to search for resources and filter by category"""

    query = forms.CharField(required=False)

    searching = forms.BooleanField(required=False)

    limit_area = forms.CharField(required=False, empty_value=None)

    expired = forms.BooleanField(required=False, initial=False)
    to_review = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.the_categories = models.Category.on_site.all()
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
class BaseResourceDetailView(DetailView):
    """Return the details of given resource"""

    model = models.Resource
    template_name = "resources/resource/details.html"
    pk_url_kwarg = "resource_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        resource = self.object

        if self.request.user.is_authenticated:
            context["bookmark"] = models.Bookmark.on_site.filter(
                resource=resource, created_by=self.request.user
            ).first()

        # If our user is responsible for a local authority, only show the
        # relevant contacts (=localized)
        context["contacts"] = resource.contacts
        if (
            not check_if_switchtender(self.request.user)
            and not self.request.user.is_anonymous
        ):
            user_projects = projects.Project.on_site.filter(
                emails__contains=self.request.user.email
            )
            if user_projects.count():
                user_depts = (
                    user_projects.exclude(commune=None)
                    .values_list("commune__department__code", flat=True)
                    .distinct()
                )
                context["contacts"] = resource.contacts.filter(
                    Q(organization__departments__in=user_depts)
                    | Q(organization__departments=None)
                )

        return context


class ResourceDetailView(BaseResourceDetailView):
    model = models.Resource
    template_name = "resources/resource/details.html"
    pk_url_kwarg = "resource_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.object

        if check_if_switchtender(self.request.user):
            context["projects_used_by"] = (
                projects.Project.on_site.filter(tasks__resource_id=resource.pk)
                .order_by("name")
                .distinct()
            )

        return context


class EmbededResourceDetailView(BaseResourceDetailView):
    model = models.Resource
    template_name = "resources/resource/details_embeded.html"
    pk_url_kwarg = "resource_id"


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
    is_switchtender_or_403(request.user)
    if request.method == "POST":
        form = EditResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.created_by = request.user
            resource.save()
            resource.sites.add(request.site)
            form.save_m2m()
            next_url = reverse("resources-resource-detail", args=[resource.id])
            return redirect(next_url)
    else:
        form = EditResourceForm()
    return render(request, "resources/resource/create.html", locals())


class EditResourceForm(forms.ModelForm):
    """Create and update form for resources"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Queryset needs to be here since on_site is dynamic and form is read too soon
        self.fields["category"] = forms.ModelChoiceField(
            queryset=models.Category.on_site.all(),
            empty_label="(Aucune)",
            required=False,
        )

        self.fields["contacts"] = forms.ModelMultipleChoiceField(
            queryset=addressbook_models.Contact.on_site.all(),
            required=False,
        )

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
        required=False,
    )
    summary = forms.CharField(
        label="Résumé bref",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": "3", "maxlength": 400}
        ),
        required=False,
    )
    tags = forms.CharField(
        label="Mots-clés",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )

    class Meta:
        model = models.Resource
        fields = [
            "title",
            "status",
            "subtitle",
            "summary",
            "tags",
            "category",
            "departments",
            "content",
            "contacts",
            "expires_on",
        ]


########################################################################
# RSS Feeds
########################################################################


class LatestResourcesFeed(Feed):
    title = "Nouvelles Ressources"
    link = "/resources/feed"
    description = "Derniers ajouts de ressources"

    def items(self):
        return models.Resource.on_site.order_by("-created_on")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    def item_link(self, item):
        return reverse("resources-resource-detail", args=[item.pk])

    def item_pubdate(self, item):
        return item.created_on


########################################################################
# bookmark resources
########################################################################


@login_required
def create_bookmark(request, resource_id=None):
    """Create bookmark for resource and and connected user"""
    resource = get_object_or_404(models.Resource, pk=resource_id)
    try:
        # look if bookmark exists and is deleted
        bookmark = models.Bookmark.deleted_on_site.get(
            resource=resource, created_by=request.user
        )
    except models.Bookmark.DoesNotExist:
        bookmark, _ = models.Bookmark.on_site.get_or_create(
            resource=resource, created_by=request.user, site=get_current_site(request)
        )
    if request.method == "POST":
        form = BookmarkForm(request.POST, instance=bookmark)
        if form.is_valid():
            # save bookmark with comments
            instance = form.save(commit=False)
            instance.site = request.site
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
            bookmark = models.Bookmark.on_site.get(
                resource_id=resource_id, created_by=request.user
            )
            bookmark.deleted = timezone.now()
            bookmark.save()
        except models.Bookmark.DoesNotExist:
            pass
    next_url = reverse("resources-resource-detail", args=[resource_id])
    return redirect(next_url)


########################################################################
# REST API
########################################################################
class ResourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows resources to be listed or edited
    """

    def get_queryset(self):
        return models.Resource.on_site.exclude(status=models.Resource.DRAFT).order_by(
            "-created_on", "-updated_on"
        )

    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticated]


# eof
