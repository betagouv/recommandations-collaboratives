# encoding: utf-8

"""
Views for resources application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-06-16 10:59:08 CEST
"""

import datetime

import reversion
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import Feed
from django.db import transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.detail import DetailView, View
from django.views.generic.edit import DeleteView
from markdownx.fields import MarkdownxFormField
from reversion.models import Version
from reversion_compare.views import HistoryCompareDetailView

from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.geomatics import models as geomatics_models
from recoco.apps.hitcount.models import HitCount
from recoco.apps.projects import models as projects
from recoco.utils import check_if_advisor, has_perm, has_perm_or_403

from . import models

########################################################################
# Searching resources
########################################################################


def resource_search(request):
    """Search existing resources"""

    form = SearchForm(request.GET)
    form.is_valid()
    query = form.cleaned_data.get("query", "")

    limit_areas = request.GET.getlist("limit_area")

    searching = form.cleaned_data.get("searching", False)

    # Get user's own departments (for "Mes départements" shortcut)
    user_departments_codes = []
    if request.user.is_authenticated and request.user.profile:
        if check_if_advisor(request.user, request.site):
            user_departments_codes = list(
                request.user.profile.departments.values_list("code", flat=True)
            )
        else:
            user_departments_codes = list(
                geomatics_models.Department.objects.filter(
                    commune__in=projects.Project.on_site.filter(
                        members=request.user
                    ).values("commune")
                ).values_list("code", flat=True)
            )

    # Auto-filter on first arrival for users with departments
    if not searching and not limit_areas and user_departments_codes:
        limit_areas = list(user_departments_codes)

    select_all_departments = not bool(limit_areas)

    categories = form.selected_categories

    resources = models.Resource.search(query, categories)

    if form.cleaned_data.get("no_category", False):
        resources = resources.filter(category__isnull=True)

    # If we are not allowed to manage resources, filter out DRAFT/TO_REVIEW items and
    # imported resources
    if not has_perm(request.user, "manage_resources", request.site):
        resources = resources.filter(status__gt=models.Resource.DRAFT).filter(
            imported_from=None
        )

    # Determine available departments based on user role
    if check_if_advisor(request.user):
        departments = geomatics_models.Department.objects.order_by("name").all()
    elif request.user.is_authenticated:
        departments = geomatics_models.Department.objects.filter(
            commune__in=projects.Project.on_site.filter(members=request.user).values(
                "commune"
            )
        )
    else:
        departments = geomatics_models.Department.objects.none()

    # Apply department filter from URL parameters
    if limit_areas:
        selected_departments_qs = geomatics_models.Department.objects.filter(
            code__in=limit_areas
        )

        if selected_departments_qs.exists():
            resources = resources.limit_area(selected_departments_qs)

    # staff can search resources
    staff_redux = Q()

    # keep draft "only" if requested
    draft = form.cleaned_data.get("draft", False)
    if draft:
        staff_redux |= Q(status=models.Resource.DRAFT)

    # keep expired "only" if requested
    expired = form.cleaned_data.get("expired", False)
    if expired:
        staff_redux |= Q(expires_on__lte=datetime.date.today())

    # keep 'to be reviewed' "only" if requested
    to_review = form.cleaned_data.get("to_review", False)
    if to_review:
        staff_redux |= Q(status=models.Resource.TO_REVIEW)

    # keep 'published' "only" if requested
    if form.cleaned_data.get("published", False):
        staff_redux |= Q(status=models.Resource.PUBLISHED)

    resources = resources.filter(staff_redux)

    category_options = [
        {"value": str(c.id), "text": str(c), "search": str(c)}
        for c in models.Category.on_site.all()
    ]

    # prefetch and select related must be after all filters, else they are useless
    resources = resources.select_related("category").prefetch_related(
        "task_recommendations"
    )

    return render(
        request,
        "resources/resource/list.html",
        {
            "resources_count": resources.count(),
            "user_bookmarks": (
                list(request.user.bookmarks.values_list("resource_id", flat=True))
                if request.user.is_authenticated
                else []
            ),
            **locals(),
        },
    )


# NOTE both using search and filter in same action is slippy


class SearchForm(forms.Form):
    """Form to search for resources and filter by category"""

    query = forms.CharField(required=False)

    searching = forms.BooleanField(required=False)

    limit_area = forms.CharField(required=False, empty_value=None)

    draft = forms.BooleanField(required=False, initial=False)
    expired = forms.BooleanField(required=False, initial=False)
    to_review = forms.BooleanField(required=False, initial=False)
    published = forms.BooleanField(required=False, initial=True)
    no_category = forms.BooleanField(required=False, initial=False)

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
            not check_if_advisor(self.request.user)
            and not self.request.user.is_anonymous
        ):
            user_projects = projects.Project.on_site.filter(members=self.request.user)

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

        if self.request.user.is_authenticated:
            context["contacts_to_display"] = list(
                HitCount.on_site.for_context_object(self.get_object())
                .for_user(self.request.user)
                .filter(
                    content_object_ct=ContentType.objects.get_for_model(
                        addressbook_models.Contact
                    ),
                )
                .distinct()
                .values_list("content_object_id", flat=True)
            )
        else:
            context["contacts_to_display"] = []

        return context


class ResourceDetailView(UserPassesTestMixin, BaseResourceDetailView):
    model = models.Resource
    template_name = "resources/resource/details.html"
    pk_url_kwarg = "resource_id"

    def test_func(self):
        resource = self.get_object()
        return resource.public or self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.get_object()

        if check_if_advisor(self.request.user):
            context["projects_used_by"] = (
                projects.Project.on_site.filter(
                    Q(tasks__resource_id=resource.pk)
                    & Q(tasks__public=True)
                    & Q(tasks__deleted=None)
                )
                .order_by("name")
                .distinct()
            )

        return context

    def get_queryset(self) -> QuerySet[models.Resource]:
        return super().get_queryset().with_ds_annotations()


class EmbededResourceDetailView(BaseResourceDetailView):
    model = models.Resource
    template_name = "resources/resource/details_embeded.html"
    pk_url_kwarg = "resource_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if task_id := self.request.GET.get("task_id"):
            context["task"] = (
                self.object.recommandations.filter(pk=task_id)
                .select_related("ds_folder")
                .first()
            )

        return context


########################################################################
# Deleting resources
########################################################################


class ResourceDeleteView(UserPassesTestMixin, DeleteView):
    model = models.Resource
    template_name = "resources/resource/delete.html"
    success_url = reverse_lazy("resources-resource-search")
    pk_url_kwarg = "resource_id"

    def form_valid(self, form):
        """
        Dereference the current site from the resource.
        When no more sites are referenced on the resource
        then mark it as deleted.
        Then redirect to the success URL.
        """
        resource = self.object

        resource.sites.remove(self.request.site)

        if resource.sites.count() == 0:
            resource.deleted = timezone.now()
            resource.save()

        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def test_func(self):
        user_has_permissions = has_perm(
            self.request.user, "sites.manage_resources", self.request.site
        )
        return user_has_permissions


########################################################################
# Creating and updating resources
########################################################################


@login_required
def resource_update(request, resource_id=None):
    """Update informations for resource"""
    has_perm_or_403(request.user, "sites.manage_resources", request.site)

    resource = get_object_or_404(models.Resource, pk=resource_id)

    if request.method == "POST":
        form = EditResourceForm(request.POST, instance=resource)

        if form.is_valid():
            needs_copy = (resource.site_origin != request.site) and (
                resource.site_origin is not None
            )

            if needs_copy:
                with transaction.atomic():
                    new_resource = resource.make_clone()
                    form.instance = new_resource

                    with reversion.create_revision():
                        reversion.set_comment(
                            f"Ressource dupliquée à l'écriture depuis {resource.site_origin.name}"
                        )
                        reversion.set_user(request.user)
                        resource.updated_on = timezone.now()
                        new_resource.site_origin = request.site
                        new_resource.sites.clear()
                        new_resource.sites.add(request.site)
                        # new_resource.save()
                        form.save()

                    resource.sites.remove(request.site)

            else:
                with reversion.create_revision():
                    resource = form.save(commit=False)
                    resource.updated_on = timezone.now()
                    resource.save()

                    reversion.set_user(request.user)
                    form.save_m2m()

            next_url = reverse("resources-resource-detail", args=[form.instance.id])
            return redirect(next_url)
    else:
        form = EditResourceForm(instance=resource)
    return render(request, "resources/resource/update.html", locals())


@login_required
def resource_create(request):
    """
    Create new resource
    """
    has_perm_or_403(request.user, "sites.manage_resources", request.site)

    if request.method == "POST":
        form = EditResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.created_by = request.user
            resource.site_origin = request.site
            with reversion.create_revision():
                reversion.set_user(request.user)
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
    support_orga = forms.CharField(label="Structure porteuse", required=False)

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
            "support_orga",
            "contacts",
            "expires_on",
        ]


# History/Reversion
class ResourceHistoryRestoreView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "sites.manage_resources"
    http_method_names = ["post"]

    def has_permission(self):
        site = get_current_site(self.request)
        return self.request.user.has_perm(self.permission_required, site)

    def post(self, request, *args, **kwargs):
        resource_id = self.kwargs.get("pk")

        resource = get_object_or_404(models.Resource, pk=resource_id)

        rev_id = self.kwargs.get("rev_pk")

        version = get_object_or_404(Version.objects.get_for_object(resource), pk=rev_id)
        with transaction.atomic(), reversion.create_revision():
            version.revert()
            reversion.set_user(request.user)
            reversion.set_comment("Restauration de version")

        messages.add_message(
            request,
            messages.SUCCESS,
            f"La version du {version.revision.date_created} a bien été restaurée.",
        )
        return redirect(reverse("resources-resource-detail", args=(resource.pk,)))


class ResourceHistoryCompareView(
    LoginRequiredMixin, PermissionRequiredMixin, HistoryCompareDetailView
):
    model = models.Resource
    permission_required = "sites.manage_resources"
    template_name = "resources/resource/history.html"

    def has_permission(self):
        site = get_current_site(self.request)
        return self.request.user.has_perm(self.permission_required, site)


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


# eof
