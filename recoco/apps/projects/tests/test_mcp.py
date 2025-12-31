# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

import pytest
from model_bakery import baker

from recoco.apps.survey import models as survey_models

from ..mcp import ProjectQueryTool


@pytest.mark.django_db
@pytest.mark.asyncio
def test_get_project(client, project, request):
    survey_session = baker.make(survey_models.Session, project=project)
    question = baker.make(
        survey_models.Question, question_set__survey=survey_session.survey
    )

    for question_set in survey_session.survey.question_sets.all():
        for question in question_set.questions.all():
            baker.make(survey_models.Answer, session=survey_session, question=question)

    tool = ProjectQueryTool()
    result = tool.get_project(id=project.pk)

    serializer_class = getattr(tool.get_project, "__dmcp_drf_serializer", None)
    if serializer_class is not None:
        ret = serializer_class(result).data

    expected = {
        "name": project.name,
        "description": project.description,
        "commune": None,
        "survey_session": [
            {
                "id": survey_session.pk,
                "survey": {
                    "id": survey_session.survey.pk,
                    "question_sets": [
                        [
                            {
                                "questions": [
                                    {"text": question.text}
                                    for question in question_set.questions.all()
                                ]
                            }
                        ]
                        for question_set in survey_session.survey.question_sets.all()
                    ],
                },
            }
        ],
    }

    assert sorted(ret) == sorted(expected)


# eof
