import time
from urllib.parse import parse_qs, urlsplit

import pytest
from allauth.socialaccount.internal.statekit import STATES_SESSION_KEY
from django.contrib.auth import models as auth_models
from django.urls import reverse
from model_bakery import baker
from waffle.testutils import override_flag

from recoco.apps.social_account.views import (
    SILENT_LOGIN_SESSION_KEY,
    SILENT_LOGIN_TRIED_SESSION_KEY,
)

SILENT_URL = reverse(
    "openid_connect_silent_login", kwargs={"provider_id": "proconnect"}
)
CALLBACK_URL = reverse("openid_connect_callback", kwargs={"provider_id": "proconnect"})
PROVIDER_LOGIN_URL = reverse(
    "openid_connect_login", kwargs={"provider_id": "proconnect"}
)
POPUP_DONE_URL = reverse(
    "openid_connect_popup_done", kwargs={"provider_id": "proconnect"}
)
STATUS_URL = reverse("openid_connect_status", kwargs={"provider_id": "proconnect"})


def _split(url):
    parts = urlsplit(url)
    return parts.path, {k: v[0] for k, v in parse_qs(parts.query).items()}


def _set_session(client, **values):
    session = client.session
    session.update(values)
    session.save()


def _stash_state(client, state_id, state):
    # mimic the state allauth stashes before redirecting to the provider
    _set_session(client, **{STATES_SESSION_KEY: {state_id: (state, time.time())}})


########################################################################
# silent_login
########################################################################


@pytest.mark.django_db
def test_silent_login_redirects_to_provider_with_prompt_none(client):
    response = client.get(SILENT_URL, {"next": "/projects/"})

    assert response.status_code == 302
    path, params = _split(response.url)
    assert path == PROVIDER_LOGIN_URL
    assert params["auth_params"] == "prompt=none"
    assert params["next"] == "/projects/"
    assert client.session[SILENT_LOGIN_SESSION_KEY] == "page"
    assert client.session[SILENT_LOGIN_TRIED_SESSION_KEY] is True


@pytest.mark.django_db
def test_silent_login_popup_mode_ends_on_popup_done(client):
    response = client.get(SILENT_URL, {"mode": "popup", "next": "/ignored/"})

    _, params = _split(response.url)
    assert params["next"] == POPUP_DONE_URL
    assert params["auth_params"] == "prompt=none"
    assert client.session[SILENT_LOGIN_SESSION_KEY] == "popup"


########################################################################
# callback
########################################################################


@pytest.mark.django_db
def test_callback_login_required_in_page_mode_goes_back_to_login(client):
    _set_session(client, **{SILENT_LOGIN_SESSION_KEY: "page"})
    _stash_state(client, "x", {"process": "login", "next": "/projects/"})

    response = client.get(CALLBACK_URL, {"error": "login_required", "state": "x"})

    assert response.status_code == 302
    path, params = _split(response.url)
    assert path == reverse("account_login")
    assert params == {"next": "/projects/"}
    assert SILENT_LOGIN_SESSION_KEY not in client.session
    assert client.session[STATES_SESSION_KEY] == {}


@pytest.mark.django_db
def test_callback_login_required_in_popup_mode_falls_back_to_interactive(client):
    _set_session(client, **{SILENT_LOGIN_SESSION_KEY: "popup"})

    response = client.get(CALLBACK_URL, {"error": "login_required", "state": "x"})

    path, params = _split(response.url)
    assert path == PROVIDER_LOGIN_URL
    assert params["next"] == POPUP_DONE_URL
    assert "auth_params" not in params


@pytest.mark.django_db
def test_callback_login_required_without_silent_marker_is_an_error(client):
    response = client.get(CALLBACK_URL, {"error": "login_required", "state": "x"})

    # allauth's authentication error page, unchanged behaviour
    assert response.status_code == 401
    assert any(
        t.name.endswith("socialaccount/authentication_error.html")
        for t in response.templates
    )


########################################################################
# popup done / status
########################################################################


@pytest.mark.django_db
@pytest.mark.parametrize("authenticated", [False, True])
def test_status(client, authenticated):
    if authenticated:
        client.force_login(baker.make(auth_models.User))

    response = client.get(STATUS_URL)

    assert response.json() == {"authenticated": authenticated}


@pytest.mark.django_db
def test_popup_done(client):
    client.force_login(baker.make(auth_models.User))

    response = client.get(POPUP_DONE_URL)

    assert response.status_code == 200
    assert b"Connexion r\xc3\xa9ussie" in response.content


########################################################################
# ProConnectSilentLoginMiddleware
########################################################################


@pytest.mark.django_db
@override_flag("proconnect_login", active=True)
def test_login_page_tries_silent_login_once(client):
    response = client.get(reverse("account_login"), {"next": "/projects/"})

    assert response.status_code == 302
    path, params = _split(response.url)
    assert path == SILENT_URL
    assert params == {"next": "/projects/"}

    # once tried, the login page is displayed
    client.get(response.url)
    response = client.get(reverse("account_login"))
    assert response.status_code == 200


@pytest.mark.django_db
@override_flag("proconnect_login", active=False)
def test_login_page_no_silent_login_without_flag(client):
    response = client.get(reverse("account_login"))

    assert response.status_code == 200


@pytest.mark.django_db
@override_flag("proconnect_login", active=True)
def test_login_page_no_silent_login_on_post(client):
    response = client.post(reverse("account_login"), {"login": "a@b.c"})

    assert response.status_code == 200


@pytest.mark.django_db
@override_flag("proconnect_login", active=True)
@override_flag("embeddable", active=True)
def test_login_page_no_silent_login_when_embedded(client):
    response = client.get(reverse("account_login"), {"embed": "1"})

    assert response.status_code == 200
    assert b"data-popup-url" in response.content


@pytest.mark.django_db
@override_flag("proconnect_login", active=True)
def test_login_page_no_silent_login_when_authenticated(client):
    client.force_login(baker.make(auth_models.User))

    response = client.get(reverse("account_login"))

    # allauth redirects authenticated users, but not to the silent login
    assert not response.url.startswith(SILENT_URL)


@pytest.mark.django_db
@override_flag("proconnect_login", active=True)
def test_other_pages_do_not_trigger_silent_login(client):
    response = client.get(reverse("home"))

    assert SILENT_LOGIN_TRIED_SESSION_KEY not in client.session
    assert response.status_code == 200
