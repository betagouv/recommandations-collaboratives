# encoding: utf-8

"""
Admin for project application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 13:55:23 CEST
"""

from csvexport.actions import csvexport
from django.contrib import admin
from django.db.models import Count, F, Q
from django.db.models.query import QuerySet
from django.http import HttpRequest
from ordered_model.admin import OrderedInlineModelAdminMixin, OrderedTabularInline

from recoco.apps.tasks import models as task_models

from . import models


class RecommendationListFilter(admin.SimpleListFilter):
    title = "Recommandations"
    parameter_name = "recommendation"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("with", "Avec reco"),
            ("with_resources", "Recos+au moins 1 resource"),
            ("without_resources", "Recos sans aucune resource"),
            ("without", "Sans reco"),
        )

    def queryset(self, request, queryset):
        if self.value() == "with":
            return queryset.exclude(tasks=None)
        if self.value() == "without":
            return queryset.filter(tasks=None)

        qs_with_tasks_count = queryset.annotate(
            tasks_count=Count("tasks"),
            tasks_nores_count=Count("tasks", filter=Q(tasks__resource=None)),
        ).exclude(tasks_count=0)

        if self.value() == "with_resources":
            return qs_with_tasks_count.filter(
                tasks_count__gt=F("tasks_nores_count")
            ).distinct()

        if self.value() == "without_resources":
            return qs_with_tasks_count.filter(
                tasks_count=F("tasks_nores_count")
            ).distinct()


class ProjectTaskTabularInline(OrderedTabularInline):
    model = task_models.Task
    fields = (
        "site",
        "intent",
        "content",
        "resource",
        "order",
        "move_up_down_links",
    )
    ordering = ("order", "site")
    readonly_fields = (
        "order",
        "move_up_down_links",
    )
    extra = 1


class ProjectMemberTabularInline(admin.TabularInline):
    model = models.ProjectMember
    fields = (
        "member",
        "is_owner",
    )
    extra = 1


class ProjectSwitchtenderTabularInline(admin.TabularInline):
    model = models.ProjectSwitchtender
    fields = (
        "switchtender",
        "is_observer",
        "site",
    )
    extra = 1


class ProjectSiteTabularInline(admin.TabularInline):
    model = models.ProjectSite
    fields = (
        "site",
        "status",
        "is_origin",
    )
    extra = 1


@admin.register(models.Project)
class ProjectAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = [
        "sites",
        "created_on",
        "exclude_stats",
        "publish_to_cartofriches",
        RecommendationListFilter,
        "tags",
    ]
    list_display = ["created_on", "name", "location"]
    actions = [csvexport]
    inlines = (
        ProjectSiteTabularInline,
        ProjectMemberTabularInline,
        ProjectSwitchtenderTabularInline,
        ProjectTaskTabularInline,
    )


@admin.register(models.UserProjectStatus)
class UserProjectStatusAdmin(admin.ModelAdmin):
    list_display = ["project", "status", "user"]

    list_select_related = ("project__commune", "user")
    readonly_fields = ("project", "user")


@admin.register(models.Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["name", "site"]
    list_display = ["name", "site"]

    def project_name(self, o):
        return o.project.name


class ShowDeletedFilter(admin.SimpleListFilter):
    title = "Is deleted"
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        return queryset.filter(deleted__isnull=not (self.value() == "yes"))


@admin.register(models.Note)
class NoteAdmin(admin.ModelAdmin):
    search_fields = [
        "content",
        "tags",
        "project__name",
    ]
    list_filter = [
        "project__sites",
        ShowDeletedFilter,
        "tags",
        "created_on",
    ]
    list_display = [
        "created_on",
        "project_name",
        "created_by",
        "is_deleted",
        "tags",
    ]
    list_select_related = ("project",)
    readonly_fields = (
        "site",
        "project",
        "created_by",
    )

    @admin.display(description="Projet")
    def project_name(self, obj: models.Note) -> str:
        return obj.project.name

    @admin.display(description="Deleted")
    def is_deleted(self, obj: models.Note) -> bool:
        return obj.deleted is not None

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Note]:
        return models.Note.all_notes.all()


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    search_fields = ["description", "the_file"]
    list_filter = ["created_on"]
    list_display = ["created_on", "description", "the_file"]
    list_select_related = ("project",)


# eof
