# encoding: utf-8

"""
Urls for dsrc application

author  : patricia.boh@beta.gouv.fr
created : 2024-03-02 01:13:25 CEST
"""


from django.urls import path

from . import views

urlpatterns = [
    path(
        r"dsrc/",
        views.dsrc,
        name="dsrc",
    ),
]

# eof
