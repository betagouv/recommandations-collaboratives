# encoding: utf-8

"""
Views for home application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-08-16 15:40:08 CEST
"""

import django.core.mail
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import models as auth
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, F, Q
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from urbanvitaliz.apps.projects import models as projects
from urbanvitaliz.utils import check_if_switchtender


class HomePageView(TemplateView):
    template_name = "home/home.html"


class StatisticsView(TemplateView):
    template_name = "home/statistics.html"

    def get_context_data(self, **kwargs):
        staff_emails = [user.email for user in auth.User.objects.filter(is_staff=True)]
        the_projects = projects.Project.objects.exclude(
            Q(email__in=staff_emails) | Q(is_draft=True) | Q(exclude_stats=True)
        )
        context = super().get_context_data(**kwargs)
        context["reco_following_pc"] = 90
        context["collectivity_supported"] = the_projects.count()
        context["collectivity_with_reco"] = (
            projects.Task.objects.filter(refused=False)
            .exclude(
                Q(project__email__in=staff_emails)
                | Q(project__is_draft=True)
                | Q(project__exclude_stats=True)
            )
            .order_by("project_id")
            .values("project_id")
            .distinct("project_id")
            .count()
        )
        numbers = [
            p.number_tasks
            for p in the_projects.all().annotate(number_tasks=Count("tasks"))
        ]
        context["collectivity_avg_reco"] = sum(numbers) / len(numbers) if numbers else 0

        context["new_col_per_month"] = [
            (f"{p['month']}/{p['year']}", p["total"])
            for p in the_projects.order_by("created_on__year", "created_on__month")
            .values(year=F("created_on__year"), month=F("created_on__month"))
            .annotate(total=Count("id"))
        ][-10:]

        context["collectivity_geo"] = (
            (p["latitude"], p["longitude"])
            for p in the_projects.exclude(commune=None).values(
                latitude=F("commune__latitude"), longitude=F("commune__longitude")
            )
        )

        return context


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


class SwitchtenderDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "staff/dashboard.html"

    def test_func(self):
        return check_if_switchtender(self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["projects_waiting"] = projects.Project.objects.filter(
            is_draft=True
        ).count()
        context["project_model"] = projects.Project
        context["user_model"] = auth.User
        return context


# eof
