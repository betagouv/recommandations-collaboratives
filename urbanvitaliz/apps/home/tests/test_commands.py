# encoding: utf-8

"""
Tests for commands of the home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-10 14:07:17 CEST
"""

import pytest
from model_bakery import baker

from django.contrib.auth import models as auth_models
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.home import models as home_models

from ..management.commands import cleanuporgs

########################################################################
# cleanup command
########################################################################


@pytest.mark.django_db
def test_cleanuporgs_merge_two_organizations():
    org_to_keep = baker.make(addressbook_models.Organization)
    org_to_merge = baker.make(addressbook_models.Organization)

    contact = baker.make(addressbook_models.Contact, organization=org_to_merge)
    user = baker.make(auth_models.User)
    profile = user.profile
    profile.organization = org_to_merge
    profile.save()

    lines = [
        (f"{org_to_merge.id}", "", f"{org_to_keep.id}", "", ""),
    ]

    cleanuporgs.process_lines(lines)

    old_org = addressbook_models.Organization.objects.filter(id=org_to_merge.id)
    assert old_org.exists() is False

    contact.refresh_from_db()
    assert contact.organization == org_to_keep

    profile.refresh_from_db()
    assert profile.organization == org_to_keep


@pytest.mark.django_db
def test_cleanuporgs_renames_an_organization():
    org = baker.make(addressbook_models.Organization)

    new_name = "New org name"

    lines = [
        (f"{org.id}", "", "", new_name, ""),
    ]

    cleanuporgs.process_lines(lines)

    org.refresh_from_db()
    assert org.name == new_name


@pytest.mark.django_db
def test_cleanuporgs_deletes_organization():
    org_to_keep = baker.make(addressbook_models.Organization)
    org_to_delete = baker.make(addressbook_models.Organization)

    lines = [
        (f"{org_to_keep.id}", "", "", "", ""),
        (f"{org_to_delete.id}", "", "", "", "ok"),
    ]

    cleanuporgs.process_lines(lines)

    old_org = addressbook_models.Organization.objects.filter(id=org_to_delete.id)
    assert old_org.exists() is False

    good_org = addressbook_models.Organization.objects.filter(id=org_to_keep.id)
    assert good_org.exists() is True



# eof
