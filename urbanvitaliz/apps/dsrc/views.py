# encoding: utf-8

"""
Base DSRC views

authors: patricia.boh@beta.gouv.fr
created: 2024-02-05 17:36:35 CEST
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, reverse

from . import forms

def init_payload(page_title: str, links: list = []):
    # Returns the common payload passed to most pages:
    # title: the page title
    # breadcrumb_data: a dictionary used by the page's breadcrumb
    # skiplinks: a list used by the page's skiplinks item

    breadcrumb_data = {
        "current": page_title,
        "links": links,
        "root_dir": "/django-dsfr",
    }

    skiplinks = [
        {"link": "#content", "label": "Contenu"},
        {"link": "#fr-navigation", "label": "Menu"},
    ]

    return {
        "title": page_title,
        "breadcrumb_data": breadcrumb_data,
        "skiplinks": skiplinks,
    }

########################################################################
# DSRC Sample Form
########################################################################

def dsrc(request):

    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = forms.DsrcExampleForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            # return HttpResponseRedirect("/thanks/")
            pass

    # if a GET (or any other method) we'll create a blank form
    else:
        form = forms.DsrcExampleForm()

    payload = init_payload(
        "Formulaire basique",
        links=[{"url": reverse("dsrc"), "title": "Formulaires"}],
    )
    payload["dsrc_example_form"] = form
    return render(request, "dsrc/samples/page_form.html", payload)

# eof
