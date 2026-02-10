# encoding: utf-8

"""
Tests for commands of the home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-10 14:07:17 CEST
"""

from io import StringIO

import pytest
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import CommandError
from model_bakery import baker

from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.home.models import SiteConfiguration
from recoco.utils import get_group_for_site, is_staff_for_site

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


@pytest.mark.django_db
def test_command_create_site_domain_already_exists(request):
    existing_site = Site.objects.first()

    command_args = {
        "name": "New site",
        "domain": existing_site.domain,
        "sender_email": "jdoe@example.org",
        "sender_name": "jdoe",
        "contact_form_recipient": "contact@example.org",
        "legal_address": "36 green street 75000 Paris",
    }

    with pytest.raises(CommandError) as exc_error:
        call_command("create_site", **command_args)

    assert f"The domain {existing_site.domain} already used" == str(exc_error.value)


@pytest.mark.django_db
def test_command_create_site_admin_user_doesnt_exists(request):
    existing_site = Site.objects.first()

    command_args = {
        "name": "New site",
        "domain": existing_site.domain,
        "sender_email": "jdoe@example.org",
        "sender_name": "jdoe",
        "contact_form_recipient": "contact@example.org",
        "legal_address": "36 green street 75000 Paris",
        "admin_user": "nobody@example.org",
    }

    with pytest.raises(CommandError) as exc_error:
        call_command("create_site", **command_args)

    assert "User matching query does not exist." in str(exc_error.value)


@pytest.mark.django_db
def test_command_create_site(request):
    admin = baker.make(auth_models.User)

    command_args = {
        "name": "New site",
        "domain": "example2.org",
        "sender_email": "jdoe@example2.org",
        "sender_name": "jdoe",
        "contact_form_recipient": "contact@example2.org",
        "legal_address": "36 green street 75000 Paris",
        "admin_user": admin.username,
    }
    out = StringIO()
    call_command("create_site", stdout=out, **command_args)
    assert (
        f"The site {command_args['name']} has been created successfully"
        in out.getvalue()
    )

    new_site = Site.objects.get(domain=command_args["domain"])
    site_config = SiteConfiguration.objects.get(site=new_site)
    assert site_config.sender_email == command_args["sender_email"]
    assert site_config.sender_name == command_args["sender_name"]
    assert site_config.contact_form_recipient == command_args["contact_form_recipient"]
    assert site_config.legal_address == command_args["legal_address"]

    assert is_staff_for_site(admin, new_site)

    # add user to check permissions
    group = get_group_for_site("advisor", new_site, create=False)
    advisor = baker.make(auth_models.User)
    advisor.profile.sites.add(new_site)
    advisor.groups.add(group)
    with settings.SITE_ID.override(new_site.pk):
        assert advisor.has_perm("sites.list_projects", new_site)


@pytest.mark.django_db
def test_command_set_needs_profile_update_with_full_profile(request):
    organization = baker.make(addressbook_models.Organization)
    user = baker.make(auth_models.User, first_name="First", last_name="Last")
    user.profile.organization = organization
    user.profile.phone_no = "0666666666"
    user.profile.organization_position = "Position"
    user.profile.save()

    call_command("set_needs_profile_update")

    user.refresh_from_db()
    assert user.profile.needs_profile_update is False


@pytest.mark.django_db
def test_command_set_needs_profile_update_with_incomplete_user(request):
    organization = baker.make(addressbook_models.Organization)
    user = baker.make(auth_models.User, first_name="", last_name="Last")
    user.profile.organization = organization
    user.profile.phone_no = "0666666666"
    user.profile.organization_position = "Position"
    user.profile.save()

    call_command("set_needs_profile_update")

    user.refresh_from_db()
    assert user.profile.needs_profile_update is True


@pytest.mark.django_db
def test_command_set_needs_profile_update_with_incomplete_userprofile(request):
    organization = baker.make(addressbook_models.Organization)
    user = baker.make(auth_models.User, first_name="First", last_name="Last")
    user.profile.organization = organization
    user.profile.phone_no = ""
    user.profile.organization_position = "Position"
    user.profile.save()

    call_command("set_needs_profile_update")

    user.refresh_from_db()
    assert user.profile.needs_profile_update is True


@pytest.mark.django_db
def test_command_set_needs_profile_update_with_incomplete_userprofile_fk(request):
    user = baker.make(auth_models.User, first_name="First", last_name="Last")
    user.profile.organization = None
    user.profile.phone_no = "0788888888"
    user.profile.organization_position = "Position"
    user.profile.save()

    call_command("set_needs_profile_update")

    user.refresh_from_db()
    assert user.profile.needs_profile_update is True


# # eof
