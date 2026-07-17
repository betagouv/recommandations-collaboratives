import pytest
from allauth.mfa.models import Authenticator
from allauth.mfa.signals import authenticator_added, authenticator_removed
from django.contrib.auth import get_user
from django.contrib.auth import models as auth_models
from django.urls import reverse
from model_bakery import baker
from sesame.utils import get_query_string

from conftest import setup_sesame_cookie
from recoco.utils import login


@pytest.mark.django_db
def test_admin_signin_should_not_be_logged(request, client):
    with login(client, is_staff=True) as user:
        assert user.actor_actions.count() == 0


@pytest.mark.django_db
def test_allauth_signin_should_be_logged(request, client):
    user = baker.make(auth_models.User, email="truc@truc.fr")
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group",
    [
        ("admin"),
        ("staff"),
    ],
)
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
    [
        ("admin"),
        ("staff"),
    ],
)
def test_no_longer_sensitive_no_2fa(request, client, group):
    user = baker.make(auth_models.User)
    group = "example_com_" + group
    group = auth_models.Group.objects.get(name=group)
    user.groups.add(group)

    user.groups.remove(group)
    assert not user.profile.requires_2fa


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group",
    [
        ("admin"),
        ("staff"),
    ],
)
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
def test_removing_totp_if_2fa_required_enables_login_by_code(request, client):
    user = baker.make(auth_models.User)
    user.profile.requires_2fa = True
    user.profile.save()
    baker.make(Authenticator, type="totp", user_id=user.id)


@pytest.mark.django_db
def test_adding_totp_disables_login_by_code(request, client):
    user = baker.make(auth_models.User)
    user.profile.login_by_code = True
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
def test_removing_totp_enables_login_by_code_sensitive_account(request, client):
    user = baker.make(auth_models.User)
    user.profile.login_by_code = False
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
def test_removing_totp_does_not_enable_login_by_code_normal_account(request, client):
    user = baker.make(auth_models.User)
    user.profile.login_by_code = False
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


SENSITIVE_GROUPS = ["admin", "staff"]


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
    # user.groups.clear()
    user = baker.make(auth_models.User)
    group = auth_models.Group.objects.get(name=f"example_com_{group_suffix}")
    user.groups.add(group)
    user.groups.clear()
    user.profile.refresh_from_db()
    assert not user.profile.requires_2fa
