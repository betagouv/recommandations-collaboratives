from django.contrib import admin
from django.contrib.sites.models import Site
from django.db.models import F, QuerySet, Value
from django.db.models.functions import Replace
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from model_clone import CloneModelAdmin

from . import models


@admin.register(models.Survey)
class SurveyAdmin(CloneModelAdmin):
    list_filter = ["site"]
    list_display = ["name", "qs_count"]

    @admin.display(description="Question Set count")
    def qs_count(self, obj):
        return obj.question_sets.count()

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Survey]:
        return super().get_queryset(request).prefetch_related("question_sets")


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["answers_count", "survey"]
    readonly_fields = ("survey", "project")

    @admin.display(description="Answers count")
    def answers_count(self, obj):
        return obj.answers.count()

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Session]:
        return super().get_queryset(request).prefetch_related("answers")


class QuestionTabularInline(admin.TabularInline):
    model = models.Question
    extra = 1


@admin.register(models.QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ["heading", "q_count", "survey"]
    inlines = (QuestionTabularInline,)

    @admin.display(description="Question count")
    def q_count(self, obj):
        return obj.questions.count()

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.QuestionSet]:
        return (
            super()
            .get_queryset(request)
            .select_related("survey")
            .prefetch_related("questions")
        )


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "text_short", "slug", "question_set"]
    list_select_related = ("question_set",)
    search_fields = ["text", "text_short", "slug"]


@admin.register(models.Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "value", "question")


class AnswerAdminSiteFilter(admin.SimpleListFilter):
    title = "site"
    parameter_name = "site"

    def lookups(self, request, model_admin):
        return [(site.id, site.name) for site in Site.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(session__project__sites=self.value())
        return queryset


class AnswerAdminWithSignalsOnlyFilter(admin.SimpleListFilter):
    title = "Avec des signaux"
    parameter_name = "with_signals_only"

    def lookups(self, request, model_admin):
        return [("oui", "oui"), ("non", "non")]

    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            trimmed_signal=Replace(
                Replace(F("signals"), Value(","), Value("")), Value(" "), Value("")
            ),
        )
        if self.value() == "oui":
            return queryset.exclude(trimmed_signal="")
        elif self.value() == "non":
            return queryset.filter(trimmed_signal="")
        return queryset


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "question_display",
        "value_display",
        "signals_display",
    )

    search_fields = (
        "question__id",
        "question__text",
        "question__slug",
    )

    list_filter = (
        AnswerAdminSiteFilter,
        AnswerAdminWithSignalsOnlyFilter,
        "created_on",
        "updated_on",
    )

    ordering = ("-updated_on",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("session", "question")
            .prefetch_related("choices")
        )

    @admin.display(description="question")
    def question_display(self, obj) -> str:
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:survey_question_change", args=[obj.question.id]),
            f"{obj.question.id} - {obj.question.text_short or obj.question.text[:100]}",
        )

    @admin.display(description="value")
    def value_display(self, obj) -> str:
        return obj.formatted_value[:100]

    @admin.display(description="signaux")
    def signals_display(self, obj) -> str:
        signals = [s.strip() for s in obj.signals.split(",")]
        return ", ".join([s for s in signals if s])
