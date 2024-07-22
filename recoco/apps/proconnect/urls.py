from django.urls import include, path

from allauth.socialaccount import app_settings

from . import views


urlpatterns = [
    path(
        "<str:provider_id>/",
        include(
            [
                path(
                    "login/",
                    views.login,
                    name="agentconnect_login",
                ),
                path(
                    "login/callback/",
                    views.callback,
                    name="agentconnect_callback",
                ),
            ]
        ),
    ),
]

if app_settings.OPENID_CONNECT_URL_PREFIX:
    urlpatterns = [
        path(
            f"{app_settings.OPENID_CONNECT_URL_PREFIX}/",
            include(urlpatterns),
        )
    ]
