from django.http import HttpResponse
from django.urls import path


def ping(request):
    return HttpResponse("pong")


urlpatterns = [
    path("plugin-testapp/ping/", ping, name="plugin-testapp-ping"),
]
