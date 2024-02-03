# encoding: utf-8

"""
views for onboarding new users/projects

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-07-17 20:39:35 CEST
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, reverse

from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects import models as projects
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
    payload["form"] = form

    return render(request, "dsrc/samples/dsrc_multistep_form.html", payload)


########################################################################
# Advisor onboard someone else
########################################################################

@login_required
def select_commune(request, project_id=None):
    """Intermediate screen to select proper insee number of commune"""
    project = get_object_or_404(projects.Project, sites=request.site, pk=project_id)
    response = redirect("survey-project-session", project_id=project.id)
    response["Location"] += "?first_time=1"
    if not project.commune:
        return response
    communes = geomatics.Commune.objects.filter(postal=project.commune.postal)
    if request.method == "POST":
        form = forms.SelectCommuneForm(communes, request.POST)
        if form.is_valid():
            project.commune = form.cleaned_data["commune"]
            project.save()
            return response
    else:
        form = forms.SelectCommuneForm(communes)
    return render(request, "onboarding/select-commune.html", locals())

# eof
