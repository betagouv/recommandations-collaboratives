import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from model_bakery import baker
import jwt


@pytest.mark.django_db
def test_obtain_token(client, request):
    user = baker.make(
        get_user_model(),
        email="anakin.skywalker@example.com",
        first_name="Anakin",
        last_name="Skywalker",
    )
    user.set_password("maytheforcebewithyou")
    user.save()

    token_url = reverse("token")
    payload = {
        "username": "anakin.skywalker@example.com",
        "password": "maytheforcebewithyou",
    }

    response = client.post(token_url, data=payload)
    assert response.status_code == 200, response.data
    token = response.json()["access"]

    decoded_token = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=["HS256"],
    )
    assert decoded_token["first_name"] == "Anakin"
    assert decoded_token["last_name"] == "Skywalker"
    assert decoded_token["email"] == "anakin.skywalker@example.com"
