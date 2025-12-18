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
def test_get_project(client, project):
    baker.make(survey_models.Session, project=project)

    tool = ProjectQueryTool()
    result = tool.get_project(id=project.pk)

    serializer_class = getattr(tool.get_project, "__dmcp_drf_serializer", None)
    if serializer_class is not None:
        ret = serializer_class(result).data

    expected = {
        "name": project.name,
        "description": project.description,
        "commune": None,
        "survey_session": [],
    }

    assert ret == expected


# eof
