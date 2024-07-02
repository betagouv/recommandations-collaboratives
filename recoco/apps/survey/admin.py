from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
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


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "value")
