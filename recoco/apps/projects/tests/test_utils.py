# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-01-18 10:11:56 CEST
"""
import pytest
from django.contrib.auth import models as auth
from django.contrib.sites import models as sites_models
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker

from recoco.apps.geomatics import models as geomatics
from recoco.apps.projects.utils import assign_advisor, assign_collaborator

from .. import models, utils


@pytest.mark.django_db
def test_get_regional_actors_for_project(client, request, make_project):
    group_current_site = auth.Group.objects.get(name="example_com_advisor")
    group_other_site, _ = auth.Group.objects.get_or_create(name="another_com_advisor")

    dept62 = baker.make(geomatics.Department, code="62")
    dept80 = baker.make(geomatics.Department, code="80")
    dept59 = baker.make(geomatics.Department, code="59")

    site = get_current_site(request)

    switchtenderA = baker.make(auth.User, groups=[group_current_site])
    switchtenderA.profile.departments.set([dept62, dept80])

    switchtenderB = baker.make(auth.User, groups=[group_current_site])
    switchtenderB.profile.departments.set([dept59, dept80])

    switchtenderC = baker.make(auth.User, groups=[group_current_site])
    switchtenderC.profile.departments.set([])

    switchtenderD = baker.make(auth.User, groups=[group_other_site])
    switchtenderD.profile.departments.set([dept59, dept62])

    project = make_project(site=site, status="READY", commune__department=dept62)

    selected_actors = utils.get_regional_actors_for_project(site, project)

    assert len(selected_actors) == 1
    assert switchtenderA in selected_actors
    assert switchtenderB not in selected_actors
    assert switchtenderC not in selected_actors
    assert switchtenderD not in selected_actors


@pytest.mark.django_db
def test_check_if_switchtends_any_project(request, client, project):
    current_site = get_current_site(request)

    group = auth.Group.objects.get(name="example_com_advisor")

    dept62 = baker.make(geomatics.Department, code="62")

    switchtender = baker.make(auth.User, groups=[group])
    switchtender.profile.departments.set([dept62])

    userA = baker.make(auth.User)
    userB = baker.make(auth.User)

    assign_advisor(userA, project, current_site)

    assert utils.can_administrate_project(project=None, user=userA)
    assert not utils.can_administrate_project(project=None, user=userB)


# get_projects_for_users
@pytest.mark.django_db
def test_get_projects_for_user_honors_draft_if_owner(request, make_project):
    current_site = get_current_site(request)

    userA = baker.make(auth.User)
    userB = baker.make(auth.User)
    project = make_project(site=current_site, status="DRAFT")

    assign_collaborator(userA, project, is_owner=True)
    assign_collaborator(userB, project)

    assert len(utils.get_projects_for_user(userA, current_site)) == 1
    assert len(utils.get_projects_for_user(userB, current_site)) == 0


@pytest.mark.django_db
def test_get_projects_for_user_honors_multisite(request, make_project):
    current_site = get_current_site(request)
    other_site = baker.make(sites_models.Site)

    user = baker.make(auth.User)
    project = make_project(status="READY")
    project.project_sites.create(site=other_site, status="DRAFT")

    assign_collaborator(user, project)

    assert len(utils.get_projects_for_user(user, current_site)) == 1
    assert len(utils.get_projects_for_user(user, other_site)) == 0


@pytest.mark.django_db
def test_assign_nonowner_collaborator_while_already_owner(request, client, project):
    member = baker.make(auth.User)

    assign_collaborator(member, project, is_owner=True)
    assign_collaborator(member, project)


@pytest.mark.django_db
def test_assign_owner_collaborator_while_already_nonowner(request, client, project):
    member = baker.make(auth.User)

    assign_collaborator(member, project, is_owner=False)
    assign_collaborator(member, project, is_owner=True)


@pytest.mark.django_db
def test_assign_owner_collaborator_while_already_another_nonowner(
    request, client, project
):
    owner = baker.make(auth.User)
    member = baker.make(auth.User)

    assign_collaborator(owner, project, is_owner=True)
    assign_collaborator(member, project, is_owner=True)

    assert project.projectmember_set.count() == 2

    owner_ms = project.projectmember_set.get(member=owner)
    member_ms = project.projectmember_set.get(member=member)

    assert owner_ms.is_owner is True
    assert member_ms.is_owner is False


########################################################################
# test for truncate string from models (to be moved to utils)
########################################################################

testdata = (
    ("", 10, ""),  # empty string
    ("abcd efg", 10, "abcd efg"),  # string smaller that max length
    ("abcd efghi", 10, "abcd efghi"),  # string equals max length
    ("abcd efg h ij", 10, "abcd efg h…"),  # last word complete
    ("abcd efgh ij", 10, "abcd efgh…"),  # backtrack to full word
)


@pytest.mark.parametrize("string,length,expected", testdata)
def test_truncate_string(string, length, expected):
    assert models.truncate_string(string, length) == expected


# eof
