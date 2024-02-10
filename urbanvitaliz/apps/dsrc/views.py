# encoding: utf-8

"""
Base DSRC views

authors: patricia.boh@beta.gouv.fr
created: 2024-02-05 17:36:35 CEST
"""

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect

from . import forms

#######################################################
# DSRC Sample Form
#######################################################

"""
This is a basic form example using the DSRC form.
"""
def dsrc_form(request):
    if request.method == "POST":
        form = forms.DsrcExampleForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL, adjust as need
            return HttpResponseRedirect("/")
        else:
            # Return the form errors
            return render(request, "dsrc/samples/page_form.html",{'dsrc_example_form': form})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = forms.DsrcExampleForm()
        return render(request, "dsrc/samples/page_form.html",{'dsrc_example_form': form})

"""
This function creates a JSON response with the form data.
It can be used in a template by an Alpine.js component to obtain the form data.
"""
def dsrc_form_data(request):
    # if a POST request, we'll process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = forms.DsrcExampleForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL, adjust as need
            return HttpResponseRedirect("/")
        else:
            # Return the form errors
            return JsonResponse({'errors': form.errors})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = forms.DsrcExampleForm()
        form_data = {field.html_name: str(field.value()) for field in form}
        # form_data = {}
        for field in form:
            value = field.value() if field.value() else ""
            form_data[field.html_name] = value
        return JsonResponse(form_data)
# eof
