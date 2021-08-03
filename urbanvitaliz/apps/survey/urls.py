# encoding: utf-8

"""
Urls for survey application

author  : guillaume.libersat@beta.gouv.fr,raphael.marvie@beta.gouv.fr
created : 2021-07-27 10:06:23 CEST
"""


from django.urls import path

from . import views

urlpatterns = [
    path(
        "projects/survey/<int:session_id>/q-<int:question_id>/",
        views.survey_question_details,
        name="survey-question-details",
    ),
    path(
        "projects/survey/<int:session_id>/",
        views.SessionDetailsView.as_view(),
        name="survey-session-details",
    ),
    path(
        "projects/survey/<int:session_id>/done",
        views.SessionDoneView.as_view(),
        name="survey-session-done",
    ),
    #
    # editor
    path(
        r"survey/editor/survey/<int:survey_id>/",
        views.editor_survey_details,
        name="survey-editor-survey-details",
    ),
    path(
        r"survey/editor/survey/<int:survey_id>/question_set/create/",
        views.editor_question_set_create,
        name="survey-editor-question-set-create",
    ),
    path(
        r"survey/editor/question_set/<int:question_set_id>/",
        views.editor_question_set_details,
        name="survey-editor-question-set-details",
    ),
    path(
        r"survey/editor/question_set/<int:question_set_id>/update/",
        views.editor_question_set_update,
        name="survey-editor-question-set-update",
    ),
    path(
        r"survey/editor/question_set/<int:question_set_id>/delete/",
        views.editor_question_set_delete,
        name="survey-editor-question-set-delete",
    ),
    path(
        r"survey/editor/question_set/<int:question_set_id>/question/create/",
        views.editor_question_create,
        name="survey-editor-question-create",
    ),
    path(
        r"survey/editor/question/<int:question_id>/",
        views.editor_question_details,
        name="survey-editor-question-details",
    ),
    path(
        r"survey/editor/question/<int:question_id>/update/",
        views.editor_question_update,
        name="survey-editor-question-update",
    ),
    path(
        r"survey/editor/question/<int:question_id>/delete/",
        views.editor_question_delete,
        name="survey-editor-question-delete",
    ),
    path(
        r"survey/editor/question/<int:question_id>/choice/create/",
        views.editor_choice_create,
        name="survey-editor-choice-create",
    ),
    path(
        r"survey/editor/choice/<int:choice_id>/update/",
        views.editor_choice_update,
        name="survey-editor-choice-update",
    ),
    path(
        r"survey/editor/choice/<int:choice_id>/delete/",
        views.editor_choice_delete,
        name="survey-editor-choice-delete",
    ),
]
