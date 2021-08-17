# encoding: utf-8

"""
Urls for survey application

author  : guillaume.libersat@beta.gouv.fr,raphael.marvie@beta.gouv.fr
created : 2021-07-27 10:06:23 CEST
"""


from django.urls import path

from .views import edit, fill

urlpatterns = [
    #
    # filling surveys
    path(
        "projects/survey/<int:session_id>/q-<int:question_id>/",
        fill.survey_question_details,
        name="survey-question-details",
    ),
    path(
        "projects/survey/<int:session_id>/q-<int:question_id>/next/",
        fill.survey_next_question,
        name="survey-question-next",
    ),
    path(
        "projects/survey/<int:session_id>/q-<int:question_id>/previous/",
        fill.survey_previous_question,
        name="survey-question-previous",
    ),
    path(
        "projects/survey/<int:session_id>/",
        fill.SessionDetailsView.as_view(),
        name="survey-session-details",
    ),
    path(
        "project/survey/<int:session_id>/results",
        fill.SessionResultsView.as_view(),
        name="survey-session-results",
    ),
    path(
        "projects/survey/<int:session_id>/start/",
        fill.survey_next_question,
        name="survey-session-start",
    ),
    path(
        "project/<int:project_id>/survey/",
        fill.survey_create_session_for_project,
        name="survey-project-session",
    ),
    path(
        "projects/survey/<int:session_id>/done",
        fill.SessionDoneView.as_view(),
        name="survey-session-done",
    ),
    #
    # editing surveys
    path(
        r"survey/editor/survey/<int:survey_id>/",
        edit.survey_details,
        name="survey-editor-survey-details",
    ),
    path(
        r"survey/editor/survey/<int:survey_id>/question_set/create/",
        edit.question_set_create,
        name="survey-editor-question-set-create",
    ),
    path(
        r"survey/editor/question_set/<int:question_set_id>/",
        edit.question_set_details,
        name="survey-editor-question-set-details",
    ),
    path(
        r"survey/editor/question_set/<int:question_set_id>/update/",
        edit.question_set_update,
        name="survey-editor-question-set-update",
    ),
    path(
        r"survey/editor/question_set/<int:question_set_id>/delete/",
        edit.question_set_delete,
        name="survey-editor-question-set-delete",
    ),
    path(
        r"survey/editor/question_set/<int:question_set_id>/question/create/",
        edit.question_create,
        name="survey-editor-question-create",
    ),
    path(
        r"survey/editor/question/<int:question_id>/update/",
        edit.question_update,
        name="survey-editor-question-update",
    ),
    path(
        r"survey/editor/question/<int:question_id>/delete/",
        edit.question_delete,
        name="survey-editor-question-delete",
    ),
    path(
        r"survey/editor/question/<int:question_id>/choice/create/",
        edit.choice_create,
        name="survey-editor-choice-create",
    ),
    path(
        r"survey/editor/choice/<int:choice_id>/update/",
        edit.choice_update,
        name="survey-editor-choice-update",
    ),
    path(
        r"survey/editor/choice/<int:choice_id>/delete/",
        edit.choice_delete,
        name="survey-editor-choice-delete",
    ),
]
