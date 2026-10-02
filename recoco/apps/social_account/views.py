from urllib.parse import urlencode

from allauth.socialaccount.internal import statekit
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache

from .adapters import CustomOpenIDConnectOAuth2Adapter

# Session keys used by the silent login flow (prompt=none)
SILENT_LOGIN_SESSION_KEY = "proconnect_silent"
SILENT_LOGIN_TRIED_SESSION_KEY = "proconnect_silent_tried"

SILENT_LOGIN_MODE_PAGE = "page"
SILENT_LOGIN_MODE_POPUP = "popup"

# errors returned by an OIDC provider when prompt=none cannot be honoured
# https://openid.net/specs/openid-connect-core-1_0.html#AuthError
SILENT_LOGIN_ERRORS = {
    "login_required",
    "interaction_required",
    "consent_required",
    "account_selection_required",
}


def login(request, provider_id):
    view = OAuth2LoginView.adapter_view(
        CustomOpenIDConnectOAuth2Adapter(request, provider_id)
    )
    return view(request)


def callback(request, provider_id):
    if request.GET.get("error") in SILENT_LOGIN_ERRORS:
        silent = request.session.pop(SILENT_LOGIN_SESSION_KEY, None)
        if silent is not None:
            return _silent_login_failed(request, provider_id, silent)

    request.session.pop(SILENT_LOGIN_SESSION_KEY, None)
    view = OAuth2CallbackView.adapter_view(
        CustomOpenIDConnectOAuth2Adapter(request, provider_id)
    )
    return view(request)


def _safe_next(request, next_url):
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


def _provider_login_url(provider_id, next_url=None, silent=False):
    params = {"process": "login"}
    if next_url:
        params["next"] = next_url
    if silent:
        params["auth_params"] = "prompt=none"
    return (
        reverse("openid_connect_login", kwargs={"provider_id": provider_id})
        + "?"
        + urlencode(params)
    )


def silent_login(request, provider_id):
    """Try to log the user in through ProConnect without any interaction.

    ProConnect answers `error=login_required` on the callback when the user
    has no active session there, see `callback`.

    In popup mode (embedded Recoco), the popup ends on `popup_done` while the
    iframe polls `status`.
    """
    mode = request.GET.get("mode")
    if mode != SILENT_LOGIN_MODE_POPUP:
        mode = SILENT_LOGIN_MODE_PAGE

    if mode == SILENT_LOGIN_MODE_POPUP:
        next_url = reverse(
            "openid_connect_popup_done", kwargs={"provider_id": provider_id}
        )
    else:
        next_url = _safe_next(request, request.GET.get("next"))

    request.session[SILENT_LOGIN_TRIED_SESSION_KEY] = True
    request.session[SILENT_LOGIN_SESSION_KEY] = {"mode": mode, "next": next_url}

    return HttpResponseRedirect(
        _provider_login_url(provider_id, next_url=next_url, silent=True)
    )


def _silent_login_failed(request, provider_id, silent):
    # drop the state stashed by allauth for the aborted login
    if state_id := request.GET.get("state"):
        statekit.unstash_state(request, state_id)

    next_url = silent.get("next")

    if silent.get("mode") == SILENT_LOGIN_MODE_POPUP:
        # we are top-level in a popup: fall back to the interactive login
        return HttpResponseRedirect(_provider_login_url(provider_id, next_url))

    url = reverse("account_login")
    if next_url:
        url += "?" + urlencode({"next": next_url})
    return HttpResponseRedirect(url)


@never_cache
def popup_done(request, provider_id):
    return render(request, "socialaccount/proconnect_popup_done.html")


@never_cache
def status(request, provider_id):
    return JsonResponse({"authenticated": request.user.is_authenticated})
