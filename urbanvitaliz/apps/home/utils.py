# encoding: utf-8

"""
Utilities for home application

authors: raphael@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-08 09:56:53 CEST
"""

from django import forms
from django.contrib.auth import models as auth


def create_user(email=None):
    """Create a new user with given email"""
    if not email:
        raise forms.ValidationError("Adresse email non reconnue")
    return auth.User.objects.create_user(email=email.lower(), username=email.lower())


# eof
