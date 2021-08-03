from django.contrib import admin

from . import models


@admin.register(models.Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ["name", "qs_count"]

    @admin.display(description="Question Set count")
    def qs_count(self, obj):
        return obj.question_sets.count()


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["answers_count"]

    @admin.display(description="Answers count")
    def answers_count(self, obj):
        return obj.answers.count()


@admin.register(models.QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ["heading", "q_count"]

    @admin.display(description="Question count")
    def q_count(self, obj):
        return obj.questions.count()


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "question_set"]


@admin.register(models.Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "value", "question")


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "value")
