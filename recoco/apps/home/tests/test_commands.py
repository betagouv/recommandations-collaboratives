# encoding: utf-8

"""
Tests for commands of the home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-10 14:07:17 CEST
"""

from datetime import datetime
from io import StringIO

import pytest
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import CommandError
from freezegun import freeze_time
from model_bakery import baker

from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.home.models import SiteConfiguration
from recoco.utils import get_group_for_site, is_staff_for_site

from ...crm.models import Note
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


# rgpd warning and deletions


@pytest.fixture()
def user_to_not_warn():
    user = baker.make(auth_models.User)
    user.profile.previous_activity_at = datetime(2025, 12, 22)
    user.profile.save()
    return user


@pytest.fixture()
def user_to_warn_once(current_site):
    user = baker.make(auth_models.User)
    user.profile.previous_activity_site = current_site
    user.profile.previous_activity_at = datetime(2023, 12, 22)
    user.profile.save()
    return user


@pytest.fixture()
def user_to_warn_twice(current_site):
    user = baker.make(auth_models.User)
    user.profile.previous_activity_site = current_site
    user.profile.previous_activity_at = datetime(2023, 12, 22)
    user.profile.nb_deletion_warnings = 1
    user.profile.previous_deletion_warning_at = datetime(2024, 12, 22)
    user.profile.save()
    return user


@pytest.fixture()
def user_came_back(current_site):
    user = baker.make(auth_models.User)
    user.profile.previous_activity_at = datetime(2025, 12, 22)
    user.profile.previous_activity_site = current_site
    user.profile.nb_deletion_warnings = 1
    user.profile.previous_deletion_warning_at = datetime(2024, 12, 22)
    user.profile.save()
    return user


@pytest.fixture()
def user_to_delete():
    user = baker.make(auth_models.User)
    user.profile.previous_activity_at = datetime(2023, 12, 22)
    user.profile.nb_deletion_warnings = 2
    user.profile.previous_deletion_warning_at = datetime(2024, 12, 22)
    user.profile.save()
    return user


@pytest.mark.django_db
def test_command_increments_warnings(
    user_to_not_warn, user_to_warn_once, user_to_warn_twice, mocker
):
    now = datetime.fromisoformat("2025-12-23T00:00:00+00:00")
    patch = mocker.patch("recoco.apps.home.utils.send_email")
    out = StringIO()
    with freeze_time(now):
        call_command("warn_delete_users", stdout=out)

    assert patch.call_count == 2

    user_to_not_warn.profile.refresh_from_db()
    user_to_warn_once.profile.refresh_from_db()
    user_to_warn_twice.profile.refresh_from_db()
    assert user_to_not_warn.profile.nb_deletion_warnings == 0
    assert user_to_not_warn.profile.previous_deletion_warning_at is None
    assert user_to_warn_once.profile.nb_deletion_warnings == 1
    assert user_to_warn_once.profile.previous_deletion_warning_at == now
    assert user_to_warn_twice.profile.nb_deletion_warnings == 2
    assert user_to_warn_twice.profile.previous_deletion_warning_at == now


@pytest.mark.django_db
@freeze_time("2025-12-23")
def test_command_forgets_warning_if_recent_activity(user_came_back, mocker):
    patch = mocker.patch("recoco.apps.home.utils.send_email")
    out = StringIO()
    call_command("warn_delete_users", stdout=out)

    assert patch.call_count == 0

    user_came_back.profile.refresh_from_db()
    assert user_came_back.profile.nb_deletion_warnings == 0
    assert user_came_back.profile.previous_deletion_warning_at is None


@pytest.mark.django_db
def test_command_dry_run_does_nothing(
    user_to_not_warn, user_to_warn_once, user_to_warn_twice, mocker
):
    now = datetime.fromisoformat("2025-12-23T00:00:00+00:00")
    patch = mocker.patch("recoco.apps.home.utils.send_email")
    out = StringIO()
    with freeze_time(now):
        call_command("warn_delete_users", stdout=out, dry_run=True)

    assert patch.call_count == 0

    assert user_to_not_warn.profile.nb_deletion_warnings == 0
    assert user_to_not_warn.profile.previous_deletion_warning_at is None
    assert user_to_warn_once.profile.nb_deletion_warnings == 0
    assert user_to_warn_once.profile.previous_deletion_warning_at is None
    assert user_to_warn_twice.profile.nb_deletion_warnings == 1
    assert user_to_warn_twice.profile.previous_deletion_warning_at != now


@pytest.mark.django_db
@freeze_time("2025-12-23")
def test_command_deletes(user_to_delete, mocker, current_site):
    EmailAddress.objects.create(user_id=user_to_delete.id)
    SocialAccount.objects.create(user_id=user_to_delete.id)
    Note.objects.create(
        related=user_to_delete, created_by=user_to_delete, site=current_site
    )

    patch = mocker.patch("recoco.apps.communication.api.send_email")
    out = StringIO()
    call_command("warn_delete_users", stdout=out)

    assert patch.call_count == 0

    user_to_delete.refresh_from_db()
    user_to_delete.profile.refresh_from_db()

    assert user_to_delete.first_name == ""
    assert user_to_delete.last_name == "Compte supprimé"
    assert user_to_delete.email == f"{user_to_delete.id}@deleted.recoconseil.fr"
    assert user_to_delete.username == f"{user_to_delete.id}@deleted.recoconseil.fr"
    assert not user_to_delete.is_active
    assert not user_to_delete.is_superuser
    assert user_to_delete.last_login is None

    assert user_to_delete.profile.phone_no == ""
    assert user_to_delete.profile.previous_activity_at is None
    assert user_to_delete.profile.previous_deletion_warning_at is None
    assert user_to_delete.profile.previous_activity_site is None
    assert user_to_delete.profile.nb_deletion_warnings == 0
    assert user_to_delete.profile.deleted is not None

    assert not EmailAddress.objects.filter(user_id=user_to_delete.id).exists()
    assert not SocialAccount.objects.filter(user_id=user_to_delete.id).exists()
    user_content_type = ContentType.objects.get_for_model(auth_models.User)
    assert not Note.objects.filter(
        content_type_id=user_content_type.id, object_id=user_to_delete.id
    ).exists()


# # eof
