import pytest
from django.contrib.auth import models as auth_models
from django.urls import reverse
from magicauth import models as magicauth_models
from model_bakery import baker
from sesame.utils import get_query_string

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
def test_magicauth_signin_should_be_logged(request, client):
    user = baker.make(auth_models.User)
    assert user.actor_actions.count() == 0
    token = baker.make(magicauth_models.MagicToken, user=user)

    url = reverse("magicauth-validate-token", args=[token.key])
    response = client.get(url)

    assert response.status_code == 302
    assert user.actor_actions.count() == 1


@pytest.mark.django_db
def test_sesame_signin_should_be_logged(request, client):
    user = baker.make(auth_models.User)
    assert user.actor_actions.count() == 0
    query = get_query_string(user)

    url = reverse("home") + query
    response = client.get(url)

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
