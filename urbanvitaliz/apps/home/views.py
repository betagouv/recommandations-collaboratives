# encoding: utf-8

"""
Views for home application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-08-16 15:40:08 CEST
"""

from django import forms

from django.shortcuts import redirect
from django.shortcuts import render

from django.views.generic.base import TemplateView


class HomePageView(TemplateView):
    template_name = "home/home.html"


def contact(request):
    """Sends an email to the team with contact info from user"""
    next_url = request.GET.get("next", "/")
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # TODO send email to team
            # TODO use message framework to notify status
            return redirect(next_url)
    else:
        form = ContactForm()
    return render(request, "home/contact.html", locals())


class ContactForm(forms.Form):

    subject = forms.CharField(max_length=256)
    content = forms.CharField(max_length=2048, widget=forms.Textarea)


# eof
