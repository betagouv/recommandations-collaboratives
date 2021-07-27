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
        "projects/survey/<int:session_id>/done",
        views.SessionDoneView.as_view(),
        name="survey-session-done",
    ),
]
