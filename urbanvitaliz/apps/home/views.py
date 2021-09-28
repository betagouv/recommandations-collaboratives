# encoding: utf-8

"""
Views for home application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-08-16 15:40:08 CEST
"""

import django.contrib.auth.models as auth_models
import django.core.mail
import urbanvitaliz.apps.projects.models as project_models
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView


class HomePageView(TemplateView):
    template_name = "home/home.html"


def contact(request):
    """Sends an email to the team with contact info from user"""
    next_url = request.GET.get("next", "/")
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            status = send_message_to_team(request, form.cleaned_data)
            notify_user_of_sending(request, status)
            return redirect(next_url)
    else:
        form = ContactForm()
    return render(request, "home/contact.html", locals())


class ContactForm(forms.Form):

    subject = forms.CharField(max_length=256)
    content = forms.CharField(max_length=2048, widget=forms.Textarea)


def send_message_to_team(request, data):
    """Send message as email to the team"""
    subject = data.get("subject")
    content = data.get("content")
    if request.user.is_authenticated:
        content += f"\n\nfrom: {request.user.email}"
    return django.core.mail.send_mail(
        subject=subject,
        message=content,
        from_email=settings.EMAIL_FROM,
        recipient_list=settings.TEAM_EMAILS,
        fail_silently=True,
    )


def notify_user_of_sending(request, status):
    """Notify user of sending request through message framework"""
    if status:
        messages.success(
            request, "Merci, votre demande a été transmis à l'équipe Urbanvitaliz !"
        )
    else:
        messages.error(
            request,
            "Désolé, nous n'avons pas réussi à envoyer votre courriel. "
            "Vous pouvez réessayer "
            "ou utiliser l'adresse depuis votre logiciel de messagerie",
        )


######
# ADMIN VIEWS
######


class StaffDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "staff/dashboard.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["projects_waiting"] = project_models.Project.objects.filter(
            is_draft=True
        ).count()
        context["project_model"] = project_models.Project
        context["user_model"] = auth_models.User
        return context


# eof
