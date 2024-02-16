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
This function returns a template view of the form.
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
            form = forms.DsrcExampleForm()
            form_data = {}
            # form_data = {}
            for field in form:
                value = field.value() if field.value() is not None else ""
                if(field.errors):
                    form_data[field.html_name] = {"errors": field.errors}
                else:
                    if field.field.widget is not None and 'message_group' in field.field.widget.attrs:
                        message_group = field.field.widget.attrs['message_group']
                    else:
                        message_group = ""
                    form_data[field.html_name] = {"value": value, "help_text": field.help_text, "message_group": message_group}
            context = {'form_data': form_data, 'dsrc_example_form': form, 'errors': form.errors}
            # Return the form errors
            return render(request, "dsrc/samples/page_form.html", context)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = forms.DsrcExampleForm()
        form_data = {}
        # form_data = {}
        for field in form:
            value = field.value() if field.value() is not None else ""
            if field.field.widget is not None and 'message_group' in field.field.widget.attrs:
                message_group = field.field.widget.attrs['message_group']
            else:
                message_group = ""
            form_data[field.html_name] = {"value": value, "help_text": field.help_text, "message_group": message_group}
        context = {'form_data': form_data, 'dsrc_example_form': form}
        return render(request, "dsrc/samples/page_form.html", context)
# eof
