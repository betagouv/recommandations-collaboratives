import pytest
from django.urls import reverse


@pytest.fixture
def openapi_schema(bot_client):
    response = bot_client.get(reverse("schema"), {"format": "json"})
    assert response.status_code == 200
    return response.json()


@pytest.mark.django_db
def test_schema_describes_service_api_keys(openapi_schema):
    scheme = openapi_schema["components"]["securitySchemes"]["serviceApiKey"]

    assert scheme["type"] == "apiKey"
    assert scheme["in"] == "header"
    assert scheme["name"] == "Authorization"


@pytest.mark.django_db
def test_schema_shows_keys_on_view_that_accepts_them(openapi_schema):
    operation = openapi_schema["paths"][reverse("auth-check")]["get"]

    assert {"serviceApiKey": []} in operation["security"]


@pytest.mark.django_db
def test_schema_does_not_show_keys_on_other_views(openapi_schema):
    operation = openapi_schema["paths"][reverse("challenge-definitions-list")]["get"]

    assert {"serviceApiKey": []} not in operation["security"]
