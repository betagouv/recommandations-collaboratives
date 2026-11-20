import pytest
from allauth.mfa.models import Authenticator
from allauth.mfa.signals import authenticator_added, authenticator_removed
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user
from django.contrib.auth import models as auth_models
from django.core import mail
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from pytest_django.asserts import assertContains
from sesame.utils import get_query_string

from conftest import setup_sesame_cookie
from recoco.apps.home.adapters import UVAccountAdapter
from recoco.apps.home.hijack import superusers_and_staff_but_not_bots
from recoco.utils import confirm_mail, login


@pytest.mark.django_db
def test_admin_signin_should_not_be_logged(request, client):
    with login(client, is_staff=True) as user:
        assert user.actor_actions.count() == 0


@pytest.mark.django_db
def test_allauth_verified_signin_should_be_logged(request, client):
    user = baker.make(auth_models.User, email="truc@truc.fr")
    confirm_mail(user)

    assert user.actor_actions.count() == 0
    password = "mon mot de passe"  # nosec B105
    user.set_password(password)
    user.save()

    url = reverse("account_login")
    response = client.post(
        url, data={"login": user.email, "password": password, "remember": False}
    )

    assert response.status_code == 302
    assert user.actor_actions.count() == 1
    assert get_user(client).is_authenticated


@pytest.mark.django_db
def test_allauth_not_verified_signin_should_not_be_logged(request, client, mocker):
    user = baker.make(auth_models.User, email="truc@truc.fr")
    assert user.actor_actions.count() == 0
    spy_adapter = mocker.spy(UVAccountAdapter, "get_email_confirmation_url")

    password = "mon mot de passe"  # nosec B105
    user.set_password(password)
    user.save()

    redirect_url = "/tata"  # intentionnally random url
    url = reverse("account_login") + f"?next={redirect_url}"
    response = client.post(
        url,
        data={"login": user.email, "password": password, "remember": False},
        follow=True,
    )

    assert get_user(client).is_anonymous
    assert user.actor_actions.count() == 0  # no login trace

    last_url, status_code = response.redirect_chain[-1]
    assert status_code == 302
    assert last_url == reverse("account_email_verification_sent")
    assertContains(response, user.email)
    assert len(mail.outbox) == 1

    confirm_email_url = spy_adapter.spy_return
    response = client.get(confirm_email_url, follow=True)
    last_url, status_code = response.redirect_chain[-1]
    assert last_url == redirect_url


@pytest.mark.django_db
def test_sesame_signin_should_be_logged(request, client):
    user = baker.make(auth_models.User)

    setup_sesame_cookie(client, user)

    assert user.actor_actions.count() == 0
    query = get_query_string(user)

    url = reverse("home") + query
    response = client.get(url)

    authenticated_user = get_user(client)
    assert authenticated_user == user
    assert response.status_code == 302
    assert user.actor_actions.count() == 1


@pytest.mark.django_db
def test_user_signin_shouldnt_be_logged_if_hijacked(request, client):
    hijacked = baker.make(auth_models.User, username="hijacked")
    assert hijacked.actor_actions.count() == 0

    with login(client, username="hijacker", is_staff=True):
        url = reverse("hijack:acquire")
        response = client.post(url, data={"user_pk": hijacked.pk})

    assert response.status_code == 302
    assert hijacked.actor_actions.count() == 0


SENSITIVE_GROUPS = ["admin", "staff", "advisor"]


@pytest.mark.django_db
@pytest.mark.parametrize("group", SENSITIVE_GROUPS)
def test_sensitive_get_2fa(request, client, group):
    user = baker.make(auth_models.User)
    group = "example_com_" + group
    group = auth_models.Group.objects.get(name=group)
    user.groups.add(group)

    user.profile.refresh_from_db()
    assert user.profile.requires_2fa
    assert user.profile.login_with_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group",
    SENSITIVE_GROUPS,
)
def test_no_longer_sensitive_no_2fa(request, client, group):
    user = baker.make(auth_models.User)
    group = "example_com_" + group
    group = auth_models.Group.objects.get(name=group)
    user.groups.add(group)

    user.groups.remove(group)
    assert not user.profile.requires_2fa


@pytest.mark.django_db
@pytest.mark.parametrize("group", SENSITIVE_GROUPS)
def test_set_requires_keeps_totp(request, client, group):
    user = baker.make(auth_models.User)
    baker.make(Authenticator, type="totp", user_id=user.id)

    group = "example_com_" + group
    group = auth_models.Group.objects.get(name=group)
    user.groups.add(group)

    user.profile.refresh_from_db()
    assert user.profile.requires_2fa
    assert not user.profile.login_with_code


@pytest.mark.django_db
def test_removing_totp_if_2fa_required_enables_login_with_code(request, client):
    user = baker.make(auth_models.User)
    user.profile.requires_2fa = True
    user.profile.save()
    baker.make(Authenticator, type="totp", user_id=user.id)


@pytest.mark.django_db
def test_adding_totp_disables_login_with_code(request, client):
    user = baker.make(auth_models.User)
    user.profile.login_with_code = True
    user.profile.save()

    authenticator_added.send(
        sender=Authenticator,
        request=request,
        user=user,
        authenticator=Authenticator.objects.create(user=user, type="totp", data="{}"),
    )
    user.profile.refresh_from_db()
    assert not user.profile.login_with_code


@pytest.mark.django_db
def test_removing_totp_enables_login_with_code_sensitive_account(request, client):
    user = baker.make(auth_models.User)
    user.profile.login_with_code = False
    user.profile.requires_2fa = True
    user.profile.save()

    authenticator_removed.send(
        sender=Authenticator,
        request=request,
        user=user,
        authenticator=Authenticator.objects.create(user=user, type="totp", data="{}"),
    )
    user.profile.refresh_from_db()
    assert user.profile.login_with_code


@pytest.mark.django_db
def test_removing_totp_does_not_enable_login_with_code_normal_account(request, client):
    user = baker.make(auth_models.User)
    user.profile.login_with_code = False
    user.profile.requires_2fa = False
    user.profile.save()

    authenticator_removed.send(
        sender=Authenticator,
        request=request,
        user=user,
        authenticator=Authenticator.objects.create(user=user, type="totp", data="{}"),
    )
    user.profile.refresh_from_db()
    assert not user.profile.login_with_code


# signals that ensure that requires_2fa is up to date


@pytest.mark.django_db
@pytest.mark.parametrize("group_suffix", SENSITIVE_GROUPS)
def test_ensure_2fa_post_add_reverse_sensitive_group_requires_2fa(group_suffix):
    user = baker.make(auth_models.User)
    group = auth_models.Group.objects.get(name=f"example_com_{group_suffix}")
    group.user_set.add(user)
    user.profile.refresh_from_db()
    assert user.profile.requires_2fa
    assert user.profile.login_with_code


@pytest.mark.django_db
@pytest.mark.parametrize("group_suffix", SENSITIVE_GROUPS)
def test_ensure_2fa_post_remove_reverse_sensitive_group_clears_2fa(group_suffix):
    # group.user_set.remove (reverse m2m)
    user = baker.make(auth_models.User)
    user.profile.requires_2fa = True
    user.profile.login_with_code = True
    user.profile.save()
    group = auth_models.Group.objects.get(name=f"example_com_{group_suffix}")
    group.user_set.add(user)
    group.user_set.remove(user)
    user.profile.refresh_from_db()
    assert not user.profile.requires_2fa
    assert user.profile.login_with_code


@pytest.mark.django_db
def test_ensure_2fa_non_sensitive_group_no_2fa_requirement():
    user = baker.make(auth_models.User)
    group = baker.make(auth_models.Group, name="regular_users")
    user.groups.add(group)
    user.profile.refresh_from_db()
    assert not user.profile.requires_2fa
    assert not user.profile.login_with_code


@pytest.mark.django_db
@pytest.mark.parametrize("group_suffix", SENSITIVE_GROUPS)
def test_ensure_2fa_pre_clear_reverse_sensitive_group_clears_2fa(group_suffix):
    # group.user_set.clear() on sensitive group
    user = baker.make(auth_models.User)
    group = auth_models.Group.objects.get(name=f"example_com_{group_suffix}")
    group.user_set.add(user)
    group.user_set.clear()
    user.profile.refresh_from_db()
    assert not user.profile.requires_2fa


@pytest.mark.django_db
def test_ensure_2fa_pre_clear_reverse_non_sensitive_group_does_not_update():
    # group.user_set.clear() on a non-sensitive group
    user = baker.make(auth_models.User)
    sensitive_group = auth_models.Group.objects.get(name="example_com_admin")
    non_sensitive_group = baker.make(auth_models.Group, name="regular_users")
    user.groups.add(sensitive_group, non_sensitive_group)
    non_sensitive_group.user_set.clear()
    user.profile.refresh_from_db()
    assert user.profile.requires_2fa


@pytest.mark.django_db
@pytest.mark.parametrize("group_suffix", SENSITIVE_GROUPS)
def test_ensure_2fa_post_clear_forward_clears_2fa(group_suffix):
    user = baker.make(auth_models.User)
    group = auth_models.Group.objects.get(name=f"example_com_{group_suffix}")
    user.groups.add(group)
    user.groups.clear()
    user.profile.refresh_from_db()
    assert not user.profile.requires_2fa


@pytest.mark.django_db
def test_becoming_a_bot_disables_password_and_email():
    user = baker.make(auth_models.User, email="bot@example.com")
    user.set_password("secret")
    user.save()
    baker.make("account.EmailAddress", user=user, email=user.email, verified=True)

    user.profile.is_bot = True
    user.profile.save()

    user.refresh_from_db()
    assert not user.has_usable_password()
    assert user.email == ""
    assert not user.emailaddress_set.exists()


@pytest.mark.django_db
def test_human_keeps_password_and_email():
    user = baker.make(auth_models.User, email="human@example.com")
    user.set_password("secret")
    user.save()
    baker.make("account.EmailAddress", user=user, email=user.email, verified=True)

    user.profile.organization_position = "maire"
    user.profile.save()

    user.refresh_from_db()
    assert user.check_password("secret")
    assert user.email == "human@example.com"
    assert user.emailaddress_set.exists()


@pytest.mark.django_db
def test_bot_cannot_login_with_its_former_password(client):
    user = baker.make(auth_models.User, username="bot", email="bot@example.com")
    user.set_password("secret")
    user.save()

    user.profile.is_bot = True
    user.profile.save()

    assert not client.login(username="bot", password="secret")  # noqa: S106


@pytest.mark.django_db
def test_setting_a_password_on_a_bot_does_not_stick(service_account, client):
    service_account.set_password("secret")
    service_account.save()

    service_account.refresh_from_db()
    assert not service_account.has_usable_password()
    assert not client.login(username=service_account.username, password="secret")  # noqa: S106


@pytest.mark.django_db
def test_setting_an_email_on_a_bot_does_not_stick(service_account):
    service_account.email = "bot@example.com"
    service_account.save()

    service_account.refresh_from_db()
    assert service_account.email == ""


@pytest.mark.django_db
def test_bot_cannot_get_an_email_address(service_account):
    baker.make("account.EmailAddress", user=service_account, email="bot@example.com")

    assert not service_account.emailaddress_set.exists()


@pytest.mark.django_db
def test_human_keeps_a_password_set_later():
    user = baker.make(auth_models.User, email="human@example.com")
    user.set_password("secret")
    user.save()

    user.refresh_from_db()
    assert user.check_password("secret")
    assert user.email == "human@example.com"


@pytest.mark.django_db
def test_bot_password_cannot_be_set_from_the_admin(service_account, client):
    admin = auth_models.User.objects.create_superuser("admin", "admin@example.com")
    with login(client, user=admin):
        client.post(
            reverse("admin:auth_user_password_change", args=[service_account.pk]),
            data={
                "usable_password": "true",
                "password1": "a-Very-long-secret-42",
                "password2": "a-Very-long-secret-42",
            },
        )

    service_account.refresh_from_db()
    assert not service_account.has_usable_password()


@pytest.mark.django_db
def test_bot_cannot_be_hijacked(service_account):
    admin = auth_models.User.objects.create_superuser("admin", "admin@example.com")
    human = baker.make(auth_models.User)

    assert not superusers_and_staff_but_not_bots(
        hijacker=admin, hijacked=service_account
    )
    assert superusers_and_staff_but_not_bots(hijacker=admin, hijacked=human)


@pytest.mark.django_db
@pytest.mark.parametrize("flag", ["is_staff", "is_superuser"])
def test_bot_cannot_be_made_staff_or_superuser(service_account, flag):
    setattr(service_account, flag, True)

    with pytest.raises(ValidationError):
        service_account.save()

    service_account.refresh_from_db()
    assert not getattr(service_account, flag)


@pytest.mark.django_db
@pytest.mark.parametrize("group_suffix", SENSITIVE_GROUPS)
def test_bot_cannot_join_sensitive_group(service_account, group_suffix):
    group = auth_models.Group.objects.get(name=f"example_com_{group_suffix}")

    with pytest.raises(ValidationError), transaction.atomic():
        service_account.groups.add(group)

    assert not service_account.groups.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("group_suffix", SENSITIVE_GROUPS)
def test_bot_cannot_be_added_to_sensitive_group_reverse(service_account, group_suffix):
    group = auth_models.Group.objects.get(name=f"example_com_{group_suffix}")
    human = baker.make(auth_models.User)

    with pytest.raises(ValidationError), transaction.atomic():
        group.user_set.add(human, service_account)

    assert not group.user_set.exists()


@pytest.mark.django_db
def test_bot_can_join_non_sensitive_group(service_account):
    trusted_bot = auth_models.Group.objects.get(name="example_com_trusted_bot")
    regular = baker.make(auth_models.Group, name="regular_users")

    service_account.groups.add(trusted_bot, regular)

    assert service_account.groups.count() == 2
    assert not service_account.profile.requires_2fa


@pytest.mark.django_db
def test_human_can_still_join_sensitive_group():
    user = baker.make(auth_models.User)
    group = auth_models.Group.objects.get(name="example_com_staff")

    user.groups.add(group)

    assert user.groups.filter(pk=group.pk).exists()


@pytest.mark.django_db
def test_bot_cannot_get_global_permissions(service_account):
    permission = auth_models.Permission.objects.get(codename="change_project")

    with pytest.raises(ValidationError), transaction.atomic():
        service_account.user_permissions.add(permission)
    with pytest.raises(ValidationError), transaction.atomic():
        permission.user_set.add(service_account)

    assert not service_account.user_permissions.exists()


@pytest.mark.django_db
def test_bot_can_get_site_object_permissions(service_account, current_site):
    assign_perm("sites.list_projects", service_account, current_site)

    assert service_account.has_perm("sites.list_projects", current_site)


@pytest.mark.django_db
def test_becoming_a_bot_drops_human_privileges():
    user = baker.make(auth_models.User, is_staff=True, is_superuser=True)
    staff = auth_models.Group.objects.get(name="example_com_staff")
    trusted_bot = auth_models.Group.objects.get(name="example_com_trusted_bot")
    user.groups.add(staff, trusted_bot)
    user.user_permissions.add(
        auth_models.Permission.objects.get(codename="change_project")
    )

    user.profile.is_bot = True
    user.profile.save()

    user.refresh_from_db()
    assert not user.is_staff
    assert not user.is_superuser
    assert not user.user_permissions.exists()
    assert list(user.groups.all()) == [trusted_bot]


@pytest.mark.django_db
def test_bot_privileges_cannot_be_given_from_the_admin(service_account, client):
    admin = auth_models.User.objects.create_superuser("admin", "admin@example.com")
    staff = auth_models.Group.objects.get(name="example_com_staff")
    with login(client, user=admin):
        response = client.post(
            reverse("admin:auth_user_change", args=[service_account.pk]),
            data={
                "username": service_account.username,
                "is_active": "on",
                "is_staff": "on",
                "groups": [staff.pk],
                "date_joined_0": "2026-01-01",
                "date_joined_1": "00:00:00",
            },
        )

    assertContains(response, "Un compte bot ne peut")
    service_account.refresh_from_db()
    assert not service_account.is_staff
    assert not service_account.groups.exists()


@pytest.mark.django_db
def test_becoming_a_bot_drops_proconnect_link_and_2fa_devices():
    user = baker.make(auth_models.User)
    baker.make(SocialAccount, user=user, provider="proconnect", uid="agent-sub")
    baker.make(Authenticator, type="totp", user=user)

    user.profile.is_bot = True
    user.profile.save()

    assert not SocialAccount.objects.filter(user=user).exists()
    assert not Authenticator.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_bot_cannot_get_a_proconnect_link(service_account):
    baker.make(
        SocialAccount, user=service_account, provider="proconnect", uid="bot-sub"
    )

    assert not SocialAccount.objects.filter(user=service_account).exists()


@pytest.mark.django_db
def test_bot_cannot_get_a_2fa_device(service_account):
    baker.make(Authenticator, type="totp", user=service_account)

    assert not Authenticator.objects.filter(user=service_account).exists()


@pytest.mark.django_db
def test_human_keeps_proconnect_link_and_2fa_devices():
    user = baker.make(auth_models.User)
    baker.make(SocialAccount, user=user, provider="proconnect", uid="agent-sub")
    baker.make(Authenticator, type="totp", user=user)

    user.profile.organization_position = "maire"
    user.profile.save()

    assert SocialAccount.objects.filter(user=user).exists()
    assert Authenticator.objects.filter(user=user).exists()
