"""Every view opened to service API keys must refuse a key whose user has no
rights at all.

Views are discovered from the URL resolver, so a view that later opts into
``ServiceAPIKeyAllowedMixin`` is covered without touching this file.
"""

import pytest
from django.contrib.auth.models import User
from django.urls import URLPattern, URLResolver, get_resolver, reverse
from model_bakery import baker

from ..authentication import ServiceAPIKeyAllowedMixin
from ..models import ServiceAPIKey

IGNORED_METHODS = {"options", "head", "trace"}


def _walk(patterns, namespace="", params=()):
    for entry in patterns:
        entry_params = params + tuple(entry.pattern.regex.groupindex)
        if isinstance(entry, URLResolver):
            ns = f"{namespace}{entry.namespace}:" if entry.namespace else namespace
            yield from _walk(entry.url_patterns, ns, entry_params)
        elif isinstance(entry, URLPattern) and entry.name:
            yield entry, f"{namespace}{entry.name}", entry_params


def _methods(callback, view_class):
    actions = getattr(callback, "actions", None)  # viewsets
    if actions:
        return sorted(set(actions) - IGNORED_METHODS)
    return sorted(
        method
        for method in view_class.http_method_names
        if method not in IGNORED_METHODS and hasattr(view_class, method)
    )


def opted_in_endpoints():
    endpoints = set()
    for pattern, name, params in _walk(get_resolver().url_patterns):
        view_class = getattr(pattern.callback, "cls", None)
        if not (view_class and issubclass(view_class, ServiceAPIKeyAllowedMixin)):
            continue
        if "format" in params:  # DRF's `.json` suffix duplicates of each route
            continue
        for method in _methods(pattern.callback, view_class):
            endpoints.add((name, tuple(sorted(set(params))), method))
    return sorted(endpoints)


OPTED_IN_ENDPOINTS = opted_in_endpoints()


def test_some_views_are_opted_in():
    # guard against the discovery silently finding nothing
    assert OPTED_IN_ENDPOINTS


@pytest.fixture
def rightless_key(current_site):
    user = baker.make(User, is_active=True)
    user.profile.is_bot = True
    user.profile.save()
    _, key = ServiceAPIKey.objects.create_key(
        name="svc-rightless", user=user, site=current_site
    )
    return key


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name,params,method",
    OPTED_IN_ENDPOINTS,
    ids=[f"{method.upper()} {name}" for name, _, method in OPTED_IN_ENDPOINTS],
)
def test_rightless_key_is_refused_everywhere(
    api_client, rightless_key, name, params, method
):
    url = reverse(name, kwargs={param: 1 for param in params})

    response = getattr(api_client, method)(
        url, HTTP_AUTHORIZATION=f"Api-Key {rightless_key}"
    )

    assert response.status_code == 403, (
        f"{method.upper()} {url} -> {response.status_code}"
    )
