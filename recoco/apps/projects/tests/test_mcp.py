# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

# from datetime import datetime
#
# import pytest
# from actstream.models import user_stream
# from django.contrib.auth import models as auth_models
# from django.contrib.sites import models as sites_models
# from django.contrib.sites.shortcuts import get_current_site
# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.urls import reverse
# from django.utils import timezone
# from freezegun import freeze_time
# from guardian.shortcuts import assign_perm
# from model_bakery import baker
# from notifications.signals import notify
# from pytest_django.asserts import assertContains
#
# from recoco import verbs
# from recoco.apps.conversations import models as conversations_models
# from recoco.apps.tasks import models as tasks_models
# from recoco.utils import login
#
# from ..mcp import ProjectQueryTool
#
########################################################################
# list of projects
########################################################################

# FIXME pourquoi est ce que ces tests n'utilisent pas le APIClient ?


# @pytest.mark.django_db
# @pytest.mark.asyncio
# def test_get_project(client, project):
#     tool = ProjectQueryTool()
#     result = yield tool.get_project(id=project.pk)
#     assert result


# eof
